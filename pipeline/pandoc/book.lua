-- pandoc filter for paper-to-book chapters.
-- Fenced divs become LaTeX environments, each tagged in the margin with where it comes from:
--   ledger=ID  -> source label + locator if the ledger check passed, a red warning if it failed
--   lean=Name  -> "Lean ✓ Name" if the Lean report verified it, otherwise "not formally checked"
-- Theorem-like blocks with no ledger= are marked UNSOURCED in red.

local status = {}
local THEOREMISH = {definition = true, theorem = true, lemma = true, proposition = true, corollary = true}
local ENV = {definition = "bdefinition", theorem = "btheorem", lemma = "blemma", proposition = "bproposition",
             corollary = "bcorollary", example = "bexample", remark = "bremark", exercise = "bexercise",
             proof = "proof", quote = "bquote", inpaper = "binpaper"}

local function str(x) return x and pandoc.utils.stringify(x) or "" end

local function set_of(list)
  local s = {}
  if list then for _, v in ipairs(list) do s[str(v)] = true end end
  return s
end

local function tex(s) return pandoc.RawInline("latex", s) end
local function texb(s) return pandoc.RawBlock("latex", s) end

local function esc(s)
  s = s:gsub("\\", "\\textbackslash{}"):gsub("([&%%$#_{}])", "\\%1"):gsub("~", "\\textasciitilde{}")
  return s
end

function Meta(m)
  local p = m.p2b or {}
  status.ledger_ok = set_of(p.ledger_ok)
  status.lean_ok = set_of(p.lean_ok)
  status.lean_checked = set_of(p.lean_checked)
  status.src = {}
  status.loc = {}
  status.label = {}
  for k, v in pairs(p.ledger_source or {}) do status.src[k] = str(v) end
  for k, v in pairs(p.ledger_locator or {}) do status.loc[k] = str(v) end
  for k, v in pairs(p.source_label or {}) do status.label[k] = str(v) end
  status.quote = {}
  for k, v in pairs(p.ledger_quote or {}) do
    status.quote[k] = str(v):gsub("%x%x", function(h) return string.char(tonumber(h, 16)) end)
  end
  return m
end

local function ledger_tag(id)
  if not id or id == "" then return nil end
  local parts = {}
  for one in id:gmatch("[^,%s]+") do
    if status.ledger_ok[one] then
      local sid = status.src[one] or "?"
      local loc = status.loc[one] or ""
      table.insert(parts, "\\srcok{" .. esc(sid) .. "}{" .. esc(loc) .. "}{" .. esc(one) .. "}")
    else
      table.insert(parts, "\\srcbad{" .. esc(one) .. "}")
    end
  end
  return table.concat(parts, "; ")
end

local function lean_tag(names)
  if not names or names == "" then return nil end
  local parts = {}
  for n in names:gsub("[\"']", ""):gmatch("[^,%s]+") do
    if status.lean_ok[n] then
      table.insert(parts, "\\leanok{" .. n .. "}")
    elseif status.lean_checked[n] then
      table.insert(parts, "\\leanbad{" .. n .. "}")
    else
      table.insert(parts, "\\leanpending{" .. n .. "}")
    end
  end
  return table.concat(parts, "; ")
end

function Div(el)
  local cls = el.classes[1]
  if not cls or not ENV[cls] then return nil end
  local ledger = el.attributes["ledger"]
  local lean = el.attributes["lean"]
  local title = el.attributes["title"]
  local env = ENV[cls]
  local notes = {}
  local lt = ledger_tag(ledger)
  if lt then table.insert(notes, lt) end
  local derived = el.attributes["derived"]
  if derived and derived ~= "" then
    local ids = {}
    for one in derived:gmatch("[^,%s]+") do
      local sid = status.src[one]
      table.insert(ids, (status.ledger_ok[one] and sid) and ("\\texttt{" .. esc(sid) .. "}") or ("\\srcbad{" .. esc(one) .. "}"))
    end
    table.insert(notes, "\\derivedtag{" .. table.concat(ids, ", ") .. "}")
    if not lean or lean == "" then table.insert(notes, "\\unsourced") end   -- derived results must be Lean-checked
  elseif THEOREMISH[cls] and (not ledger or ledger == "") then table.insert(notes, "\\unsourced") end
  local nt = lean_tag(lean)
  if nt then table.insert(notes, nt) end
  -- notes go to the foot of the page: a marker here, the text queued until the outermost box closes
  local open = "\\bpush\\begin{" .. env .. "}" .. (title and ("[" .. esc(title) .. "]") or "")
  if el.identifier ~= "" then open = open .. "\\label{" .. el.identifier .. "}" end
  local notetex = #notes > 0 and ("\\srcnote{" .. table.concat(notes, " \\enspace\\textperiodcentered\\enspace ") .. "}") or nil
  -- every marker goes in front: after a block's heading, or opening the first line of a quotation
  if notetex and cls ~= "quote" then open = open .. notetex end
  local blocks = {texb(open)}
  -- index the term a definition introduces (its first bold text)
  if cls == "definition" then
    local term
    el:walk({Strong = function(s) if not term then term = str(s) end end})
    if term then table.insert(blocks, texb("\\index{" .. esc(term) .. "}")) end
  end
  -- an empty quote block is filled with the ledger's verified quotation, verbatim
  if cls == "quote" and #el.content == 0 and ledger and status.quote[ledger] then
    local q = status.quote[ledger]
    if status.ledger_ok[ledger] then
      local ok, doc = pcall(pandoc.read, q, "markdown+tex_math_dollars")
      if ok and doc.blocks[1] then
        for _, b in ipairs(doc.blocks) do table.insert(blocks, b) end
      else
        table.insert(blocks, pandoc.Para({pandoc.Str(q)}))
      end
    else
      table.insert(blocks, texb("\\srcbad{" .. esc(ledger) .. "}"))
    end
  end
  for _, b in ipairs(el.content) do table.insert(blocks, b) end
  if notetex and cls == "quote" then
    local placed = false
    for k = 2, #blocks do
      local b = blocks[k]
      if b.t == "Para" or b.t == "Plain" then
        table.insert(b.content, 1, pandoc.RawInline("latex", notetex))
        placed = true
        break
      end
    end
    if not placed then blocks[1] = texb(blocks[1].text .. notetex) end
  end
  table.insert(blocks, texb("\\end{" .. env .. "}\\bpop"))
  return blocks
end

-- [@L0012] cites a ledger entry's source. Citations are taken out of the sentence and one
-- marker is put at the start of the paragraph, so a marker can never sit after a formula.
local function cite_text(id)
  local sid = status.src[id]
  if sid and status.ledger_ok[id] then
    return "\\srccite{" .. esc(sid) .. "}{" .. esc(status.loc[id] or "") .. "}"
  elseif sid then
    return "\\srcbad{" .. esc(id) .. "}"
  end
  return "\\textcolor{unsourced}{[no ledger entry " .. esc(id) .. "]}"
end

local function lift_cites(el)
  local found, out = {}, {}
  for _, x in ipairs(el.content) do
    if x.t == "Cite" then
      for _, ci in ipairs(x.citations) do table.insert(found, cite_text(ci.id)) end
      if #out > 0 and (out[#out].t == "Space" or out[#out].t == "SoftBreak") then table.remove(out) end
    else
      table.insert(out, x)
    end
  end
  if #found == 0 then return nil end
  table.insert(out, 1, pandoc.RawInline("latex", "\\srccitenote{" .. table.concat(found, "; ") .. "}"))
  el.content = out
  return el
end

return {{Meta = Meta}, {Para = lift_cites, Plain = lift_cites}, {Div = Div}}
