# DeepSeek / Qwen Classification-and-Cleaning Prompt

This is the structured prompt used in Appendix B.4 to screen each candidate policy entry
for open science relevance and to clean the retained text in a single call.

- **Prompt version:** `open_action_academic_resources_v11`
- **Models:** DeepSeek-V4 (flash and pro) and Qwen-3.5 (flash and plus), applied across batches
- **Source script:** `dataprocess_codex/clean_policy_items_with_deepseek.py`
- **Output:** strict JSON; each entry receives a binary open science judgement (`是` / `否`)
  and, when retained, a cleaned text
- **Note:** the prompt was written in Chinese because the policy texts are Chinese. The
  English version below is a faithful translation provided for international readers.

---

## 1. Chinese version (as used)

### System prompt

```
你是开放科学政策文本清理助手。只输出JSON。目标是从输入政策条目中整理出清爽、可读、聚焦开放科学的政策文本。原则：不概括、不扩写、不改变原意；只做删除、去序号、去无关标题、必要的换行拼接。
```

### User prompt

```
任务：
1 判断输入中是否存在开放科学相关政策内容。开放科学范畴包括：开放获取；开放数据；开源代码软件；开放教育资源；公众科学；开放同行评审；开放基础设施；开放研究方法。
2 判断标准不是简单关键词匹配。只有当政策文本明确表达对科学、科研、学术、教育或知识传播相关对象进行开放、公开、共享、开源、开放获取、开放使用或开放复用时，才属于开放科学。
3 相关对象包括但不限于科研知识、科研数据、科研资源、学术资源、教育资源、课程资源、科研软件、实验室、科研设施、科学仪器、科研基础设施、研究过程/方法、科学传播、学术交流、公众参与等。对象范围要覆盖自然科学、社会科学、教育研究和跨学科学术活动。
4 单独出现"资源、数据、平台、信息化、获取、一网通办、政府信息公开"等词，不足以判定为开放科学；必须看它们是否与科学/科研/学术/教育/知识传播相关对象，以及开放、公开、共享、开源等开放性动作构成明确关系。
5 例：开放实验室、开放科研设施、共享学术资源、促进学术资源共享、公开科研数据、共享教育资源、开源科研软件、开放课程资源、公众科学传播等，均应保留相关完整文本。普通政务服务便利化或一般信息化建设不因"平台/获取/一网通办"等词而自动相关。
6 processed_item只保留开放科学相关的完整政策段落或完整条目片段，不要句子级碎片。如果相关内容本身是一整段，保留完整段落；如果相关内容只是并列任务中的一个完整子项，保留该完整子项。
7 删除无关背景、无关标题、其他政策任务、责任分工、牵头单位、配合单位、联系人、完成时限、页码等内容。删除前置序号、条号和目录号，使文本清爽可读。
8 默认只输出1个item。只有同一输入中存在多个相互独立、可单独成条的开放科学政策规定，且合并会造成主题混杂时，才拆成多个items。
9 不要概括、不要解释、不要新增事实、不要改变原意。只允许删除无关内容、去除序号、整理空白和换行。
10 如果没有开放科学相关内容，返回空数组；程序会在Excel中将处理后文本留空并标注"否"。
只返回：
{
  "items": [
    {
      "processed_item": "清理后的单条开放科学相关政策文本",
      "is_open_science": "是"
    }
  ]
}
输入：
{policy_item}
```

---

## 2. English version (translation)

### System prompt

```
You are an assistant for cleaning open science policy texts. Output JSON only. The goal is
to extract clean, readable, open science-focused policy text from each input policy entry.
Principle: do not summarise, do not expand, do not change the original meaning; only delete
content, remove numbering, remove irrelevant headings, and join lines where necessary.
```

### User prompt

```
Task:
1. Judge whether the input contains open science-related policy content. The open science
   categories are: open access; open data; open-source code and software; open educational
   resources; citizen science; open peer review; open infrastructure; open research methods.
2. The criterion is not simple keyword matching. An entry belongs to open science only when
   the policy text explicitly expresses opening, disclosing, sharing, open-sourcing, open
   access, open use, or open reuse of objects related to science, research, scholarship,
   education, or knowledge dissemination.
3. Relevant objects include but are not limited to research knowledge, research data,
   research resources, scholarly resources, educational resources, course resources,
   research software, laboratories, research facilities, scientific instruments, research
   infrastructure, research processes and methods, science communication, scholarly
   exchange, and public participation. The scope covers the natural sciences, the social
   sciences, education research, and interdisciplinary scholarly activity.
4. Words such as "resource", "data", "platform", "informatization", "access", "one-stop
   government service", or "government information disclosure" appearing alone are not
   sufficient to classify an entry as open science. They count only when they form an
   explicit relation with a science, research, scholarship, education, or knowledge-
   dissemination object and with an opening action such as opening, disclosing, sharing,
   or open-sourcing.
5. Examples: open laboratories, open research facilities, shared scholarly resources,
   promoting the sharing of scholarly resources, disclosing research data, sharing
   educational resources, open-source research software, open course resources, and public
   science communication should all be retained as complete relevant text. Ordinary
   administrative-service convenience or general informatization construction does not
   become relevant simply because words like "platform", "access", or "one-stop service"
   appear.
6. processed_item keeps only the complete open science-related policy paragraph or the
   complete clause fragment, not sentence-level fragments. If the relevant content is
   itself a whole paragraph, keep the whole paragraph; if it is one complete sub-item among
   parallel tasks, keep that complete sub-item.
7. Delete irrelevant background, irrelevant headings, other policy tasks, responsibility
   assignments, lead units, supporting units, contact persons, deadlines, page numbers, and
   similar content. Remove leading serial numbers, article numbers, and table-of-contents
   numbers so that the text reads cleanly.
8. By default output only one item. Split into multiple items only when the same input
   contains several mutually independent open science policy provisions that can each stand
   alone and whose merging would mix topics.
9. Do not summarise, do not explain, do not add facts, do not change the original meaning.
   Only deletion, removal of numbering, and the tidying of whitespace and line breaks are
   allowed.
10. If there is no open science-related content, return an empty array; the program then
    leaves the processed text blank and marks the entry as "no".

Return only:
{
  "items": [
    {
      "processed_item": "the cleaned single open science-related policy text",
      "is_open_science": "是"
    }
  ]
}
Input:
{policy_item}
```

Note: `is_open_science` takes the Chinese values `是` (yes) or `否` (no). `{policy_item}` is
the placeholder into which each candidate entry is inserted at run time.
