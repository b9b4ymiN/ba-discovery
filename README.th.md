# BA Discovery

[English](README.md) | [ไทย](README.th.md)

**ทำ Business Analysis ให้ถูกก่อน แล้วค่อยให้ Agent ไปสร้าง Software ให้ดี**

Coding Agent ทุกวันนี้เก่งขึ้นมากในการเปลี่ยนแผนที่ชัดเจนให้กลายเป็นโค้ดที่ใช้งานได้ ปัญหาที่ยากกว่ามักเกิดก่อนถึงขั้นเขียนโค้ด: เรายังไม่เข้าใจปัญหาจริง, Stakeholder กับ Agent เข้าใจคนละอย่าง, Scope ขยับไปมา หรือ Agent เริ่มออกแบบ Solution ก่อนที่ทุกคนจะตกลงกันด้วยซ้ำว่า “สำเร็จ” หมายถึงอะไร

BA Discovery คือชุด Business Analysis skills แบบ modular สำหรับ Claude Code ช่วยพา Project จาก **Background → Goal → Scope → Requirements → System Design → FRD** และเก็บเหตุผล/ข้อตกลงที่สำคัญไว้เป็น durable project state ใน repo เพื่อให้ session หรือ agent ถัดไปรับช่วงต่อได้โดยไม่ต้องเริ่มเล่าใหม่ตั้งแต่ต้น

มันตั้งใจ **ไม่เป็น Coding Workflow**

เมื่อ Business Problem และสิ่งที่ควรสร้างชัดพอแล้ว งานควรถูกส่งต่อเข้าสู่ Engineering Workflow ต่อไป README นี้แนะนำการต่อยอดด้วย [mattpocock/skills](https://github.com/mattpocock/skills)

---

## ทำไมควรเริ่มจากตรงนี้?

Engineering workflow ที่ดีมาก ๆ ก็ยังสามารถสร้าง “ของผิดชิ้น” ได้อย่างมีประสิทธิภาพ

BA Discovery ถูกสร้างขึ้นเพื่อลด failure modes หลักที่มักเกิด **ก่อนเริ่ม implementation**

### #1: Agent รีบแก้ปัญหาก่อนที่จะเข้าใจปัญหา

User พูดว่า “เราอยากได้ planning system ที่ดีกว่านี้” แล้ว Agent ก็เริ่มเสนอ architecture, database, queue หรือ UI ทันที

สิ่งที่หายไปคือการเข้าใจสถานการณ์ปัจจุบัน:

- Project นี้เกิดขึ้นทำไม?
- วันนี้อะไรคือ pain point จริง?
- Outcome แบบไหนที่มีความหมายกับธุรกิจ?
- ในระบบเดิมมีอะไรที่เป็น fact อยู่แล้ว?
- อะไรอยู่ใน scope และอะไรอยู่นอก scope?

BA Discovery เริ่มจากตรงนี้ แทนที่จะถือว่า idea แรกของ User คือ requirement ที่ถูกต้องแล้ว

### #2: User ถูกถามคำถามที่ตัวเองตอบอย่างมีความหมายไม่ได้

คำถามที่ technical ถูกต้อง ไม่ได้แปลว่าเป็นคำถาม BA ที่ดี

Stakeholder อาจเข้าใจธุรกิจของตัวเองลึกมาก แต่ไม่จำเป็นต้องรู้ว่าระบบควรใช้ event sourcing, MVVM, graph database หรือ integration pattern แบบใด ถ้าเราบังคับให้เขาเลือก เราจะได้ “ความมั่นใจปลอม” มากกว่าความต้องการจริง

BA Discovery จะแยกว่า:

- เรื่องไหน Stakeholder คือ source ที่ถูกต้อง,
- เรื่องไหนควรอ่านจาก codebase หรือเอกสาร,
- เรื่องไหนควร research,
- และเรื่องไหนควรปล่อยให้ Engineering ตัดสินใจภายหลัง

เป้าหมายไม่ใช่คุยให้น้อยที่สุด แต่คือ **ลดบทสนทนาที่ซ้ำซ้อนหรือเป็นคำถามที่ User ตอบไม่ได้จริง**

### #3: Requirement ค่อย ๆ เพี้ยนเมื่อเปลี่ยน Session

Conversation ยาว ๆ ไม่ใช่ durable project state

BA Discovery เก็บ **Project Brain** แบบเบา ๆ ไว้ใน Project ที่กำลังวิเคราะห์:

```text
.ba/
├── PROJECT.md
├── REQUIREMENTS.md
├── DECISIONS.md
├── RESEARCH.md
└── phases/
```

Conversation จบได้ แต่ Project ไม่จำเป็นต้องลืม

Approved phase snapshots เก็บสิ่งที่ตกลงไว้ในช่วงเวลานั้น ส่วน canonical files เก็บ current truth ล่าสุดที่ยัง valid

### #4: Spec ที่ดี ก็ยังอาจอธิบาย “ปัญหาผิดเรื่อง”

Engineering Spec จะแข็งแรงที่สุดเมื่อ decision ที่ป้อนเข้าไปเชื่อถือได้แล้ว

BA Discovery จึงโฟกัสคำถามที่มาก่อน implementation:

> เราทำ Project นี้ไปทำไม?
>
> เราต้องการผลลัพธ์อะไร?
>
> Scope ที่แท้จริงคืออะไร?
>
> ระบบต้องทำอะไรบ้าง?
>
> Business Rules และ Constraints ไหนเป็นของจริง?
>
> Decision ไหน approve แล้ว และอะไรยังเป็น assumption?

นี่คือ boundary ที่ Project นี้รับผิดชอบ

---

## BA Flow

คุณใช้ครบทั้ง flow ก็ได้ หรือเรียกเฉพาะ phase ที่ต้องการก็ได้

```text
Idea / Existing System
        │
        ▼
     /ask-ba
        │
        ▼
   /ba-discovery
        │
        ├── Understand
        │      Background
        │      Problem
        │      Goal
        │      Current state
        │
        ├── Requirements
        │      Needs
        │      Constraints
        │      Evidence
        │      Business rules
        │
        ├── Design
        │      System logic
        │      Boundaries
        │      Workflows
        │      Decisions
        │
        ├── Final FRD
        │
        └── Professional Report
```

แต่ละ Phase แยกเป็น Skill อิสระ คุณจึงไม่จำเป็นต้องทำทุกอย่างใน session เดียว

| Skill | ใช้เมื่อ |
|---|---|
| `ask-ba` | ยังไม่แน่ใจว่าควรเริ่มตรงไหน หรือควรใช้ BA skill ตัวใด |
| `ba-discovery` | อยากให้ Pipeline พาเดินผ่านหลาย BA phases |
| `ba-understand` | Background, ปัญหาจริง, Goal หรือ Current State ยังไม่ชัด |
| `ba-requirements` | เข้าใจปัญหาแล้ว และต้องการค้นหา/validate ว่าระบบต้องทำอะไร |
| `ba-design` | Requirement ชัดพอแล้ว และต้องการออกแบบ System Logic / Design |
| `ba-spec` | Decision หลักนิ่งแล้ว และต้องการ Final FRD แบบ consolidated |
| `ba-report` | ต้องการ Professional ELI5-style Project Report ที่คนทั่วไปอ่านเข้าใจได้ |

Prerequisite ของแต่ละ Phase เป็น **Soft Guard** ไม่ใช่กำแพงบังคับ ถ้าคุณมี approved requirements จากแหล่งอื่นอยู่แล้ว คุณเข้า `ba-design` ได้โดยตรง BA Discovery จะเก็บ provenance ไว้ตามจริง แทนที่จะแกล้งทำว่า Phase ก่อนหน้าเคยเกิดขึ้น

---

## คุณภาพของคำถามเป็นส่วนหนึ่งของ Product

BA Discovery ถือว่า “การออกแบบคำถาม” เป็น Core Behavior ไม่ใช่แค่เรื่องน้ำเสียง โดยใช้ **Question Contract** ร่วมกันทุก Phase เพื่อเลือกว่าควรถามใคร, เรื่องไหนควรอ่านจาก artifact หรือ research เอง, ต้องอธิบายมากแค่ไหน และควรตีความคำตอบอย่างไรก่อนเก็บเป็น durable truth

- **Decision-critical** questions ถามทีละเรื่อง เพื่อให้คำตอบข้อหนึ่งเปลี่ยนคำถามถัดไปได้
- factual questions ที่เกี่ยวกันและความเสี่ยงต่ำรวมได้ 2–4 ข้อ ถ้าคำตอบไม่กระทบกัน
- ไม่โยน expert reasoning ด้าน architecture ให้ Stakeholder ที่ไม่ได้เป็นเจ้าของ decision นั้น
- คำตอบประมาณการยังคงเป็น estimate จนกว่าจะมีการยืนยันเป็น hard requirement จริง
- แสดง progress แบบ qualitative ไม่สร้างเปอร์เซ็นต์ความคืบหน้าปลอม

หลักสั้น ๆ คือ **ถามให้ดี แล้วเก็บคำตอบตามความจริง**

## บทบาทของ Project Brain

Project Brain แยกข้อมูลออกเป็น 4 บทบาท เพื่อไม่ให้ summary ค่อย ๆ กลายเป็น source of truth แข่งกันเอง:

- **CANONICAL** — current project truth เช่น Problem, Goal, Scope, Requirements, Constraints และ Decisions
- **EVIDENCE** — research/source synthesis ที่ใช้ประกอบการตัดสินใจ แต่ไม่กลายเป็น requirement อัตโนมัติ
- **DERIVED / NAVIGATION** — current phase, baseline, coverage และ Next Focus ซึ่งเป็น projection ไม่ใช่ truth บ้านที่สอง
- **HISTORICAL** — approved phase snapshots ที่บอกว่า ณ เวลานั้นเราอนุมัติอะไรไว้

Approved snapshot เป็น append-only; current truth เปลี่ยนได้ แต่เราไม่ rewrite history เพื่อทำให้ Project ดูสะอาดขึ้น

## Change Management ใน v0.8

`/ba-change` เป็น Single Front Door สำหรับเปลี่ยน Project Truth ที่เคย approve แล้ว โดยไม่ปล่อยให้สิ่งที่ยังคิดอยู่ปนเข้า current truth ระบบนี้เป็น **Single User Only** เสมอ: ผู้ใช้คนเดิมเป็นคนให้ business intent, clarification, impact confirmation และ final confirmation ส่วน role ต่าง ๆ ที่อยู่ “ภายในระบบที่กำลังออกแบบ” ไม่ได้กลายเป็นผู้ใช้งาน BA workflow เพิ่มขึ้น

State แบ่งหน้าที่ชัดเจน:

- **Current canonical** — ความจริงล่าสุดที่ approve แล้ว
- **Pending change** — working analysis ที่เก็บถาวรใน `.ba/changes/CHG-*.md` แต่ยังไม่ใช่ approved truth
- **Applied change** — อธิบายว่าทำไม current truth ถึงเปลี่ยน
- **Phase snapshot** — เก็บว่า ณ milestone ก่อนหน้าเราเคย approve อะไร

กฎหลักคือ:

> **Stage the change, commit the truth.**
>
> **Current truth for work. History on demand.**

เมื่อมี intent ใหม่เข้ามา BA จะเปิดอ่าน OPEN change ที่มีอยู่จริงก่อน (**Read before relating**) แล้วเทียบกันที่ business intent ไม่ใช่แค่ keyword หรือ component ที่เหมือนกัน จากนั้นค่อย trace Impact Frontier ตาม causal evidence และทำ Minimum Revalidation เฉพาะเรื่องที่ต้องแก้หรือยืนยันใหม่จริง ๆ

ก่อนแก้ canonical truth ผู้ใช้จะเห็นสรุป **Before → After** เป็นภาษาที่เข้าใจได้ แล้ว deterministic tooling จะตรวจ prospective state, commit, อ่านกลับมาตรวจอีกครั้ง และค่อยถือว่า Change เป็น `APPLIED`

ตัวอย่าง: MOQ จากค่าคงที่เดียวไปเป็นตาม Package Size อาจยังเป็น Change เดียวกัน แม้จะมีรายละเอียดเพิ่มเรื่อง Package Size ที่ไม่มี MOQ, Below-MOQ handling หรือการรวม Order เพื่อให้ผ่าน MOQ เพราะทั้งหมดกำลังนิยาม business concern เรื่อง MOQ เดียวกันใหม่

## `/ask-ba` บอกได้ด้วยว่า “ไม่ต้องทำ BA ต่อ”

`/ask-ba` ไม่จำเป็นต้อง route กลับเข้า BA phase เสมอ มันมี 3 outcome หลัก:

- **BA capability** — ยังมี business/requirement uncertainty ที่ควรทำ BA ต่อ
- **Engineering workflow** — business/specification boundary ชัดพอแล้ว งานถัดไปคือ planning, coding, testing, review หรือ handoff
- **No BA needed** — งานเล็ก ชัด และ bounded อยู่แล้ว การเพิ่ม BA ceremony ไม่ได้ลด uncertainty ที่มีความหมาย

แบบนี้ BA Discovery จะยังโฟกัสหน้าที่จริงของ BA และไม่พยายามครอบ software lifecycle ทั้งหมด

## Quick Start

Clone หรือ download repository นี้ แล้วโหลดเป็น Claude Code plugin:

```bash
claude --plugin-dir /path/to/ba-discovery
```

Canonical plugin commands จะมี namespace:

```text
/ba-discovery:ask-ba
/ba-discovery:ba-discovery
/ba-discovery:ba-understand
/ba-discovery:ba-requirements
/ba-discovery:ba-design
/ba-discovery:ba-spec
/ba-discovery:ba-report
/ba-discovery:ba-change
```

ตัวอย่างเริ่มต้นง่ายที่สุด:

```text
/ba-discovery:ask-ba
ผมมีระบบ planning เดิมอยู่แล้ว แต่ยังไม่แน่ใจว่าควรเริ่มจาก problem, requirements หรือ design
```

หรือให้ Pipeline พาไป:

```text
/ba-discovery:ba-discovery
พา Project นี้ไปจนถึง System Design แต่หยุดให้ผม approve ทุก phase
```

หรือเข้าความสามารถเฉพาะทางโดยตรง:

```text
/ba-discovery:ba-design
ใช้ approved requirements ใน docs/requirements.md เป็น input สำหรับ design
```

หยุดได้ตามธรรมชาติ และกลับมาต่อได้ตามธรรมชาติ Project Brain เป็นตัวเก็บ continuity ให้กับงาน

---

## BA Discovery สร้างอะไรให้ Project?

เป้าหมายไม่ใช่สร้างเอกสารให้เยอะที่สุด แต่คือทิ้ง **approved, traceable project truth** ไว้มากพอที่ downstream agent จะไม่ต้องพยายาม reconstruct เหตุผลทั้งหมดจาก chat history

Output โดยทั่วไปประกอบด้วย:

- Background, Problem และ Goal ของ Project,
- Scope และ Non-goals ที่ชัดเจน,
- Requirements และ Constraints ที่ validate แล้ว,
- Material Decisions พร้อมเหตุผล,
- Research findings พร้อม provenance,
- System Logic และ Design,
- Approved phase snapshots,
- Final FRD,
- และ Professional FRD Report สำหรับ Business Reader เมื่อจำเป็น

### Professional Report

`ba-report` ใช้ pattern คงที่ชื่อ `BA-ELI5-FRD v1.0` เพื่อให้ Report ของทุก Project คุ้นเคยและเปรียบเทียบกันได้:

1. Background
2. Goal
3. What We Will Do
4. Scope & Boundaries
5. Current → Future
6. Project / System Logic
7. Functional Requirements
8. Business Rules & Decision Logic
9. Data & Integrations
10. Roles, Responsibilities & Permissions
11. Exceptions & Edge Cases
12. Non-Functional Requirements
13. Acceptance & Success Criteria
14. Risks, Assumptions & Open Items
15. Technical Reference & Traceability

Report เป็น **presentation layer บน approved project truth** เท่านั้น ห้ามสร้าง requirement ใหม่หรือแก้ contradiction แบบเงียบ ๆ เพื่อทำให้รายงานดูครบ สำหรับ HTML จะเริ่มจาก fixed shell ที่ `skills/ba-report/assets/report-template.html` เพื่อให้ typography, section layout, callout, traceability และ print behavior เหมือนกันทุก Project

---

## Optional Companion: ELI5

BA Discovery มี **Answerability Gate** และหลักการ transform คำถามของตัวเองอยู่แล้ว Stakeholder ไม่ควรต้องติดตั้ง Skill เพิ่มเพียงเพื่อให้เข้าใจคำถามที่ BA Discovery ถาม และ `ba-report` ต้องสร้าง `BA-ELI5-FRD` มาตรฐานของมันเองได้โดยไม่พึ่ง Skill ภายนอก

ดังนั้น [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5) คือ **Skill ที่แนะนำ แต่ไม่จำเป็นต้องติดตั้ง**

มันเหมาะเมื่อเรามี approved project truth แล้ว แต่ต้องการอธิบายเรื่องเดียวกันให้คนต่างกลุ่มเข้าใจ:

```text
BA Discovery
ค้นหาและรักษา Project Truth
        │
        ├── /ba-report
        │   Standard Professional Project Report
        │
        └── ELI5 (optional)
            ปรับคำอธิบายให้เหมาะกับ Audience เฉพาะกลุ่ม
```

ตัวอย่าง:

```text
อธิบาย architecture นี้ให้ Production Manager เข้าใจ
อธิบาย REQ-024 ให้ผู้บริหารที่ไม่ใช่สายเทคนิค
อธิบายว่าทำไม Project นี้ใช้ Graph Database ให้ Planner เข้าใจ
```

Boundary ที่ควรจำคือ:

> **BA Discovery ค้นหาและรักษาความจริงของ Project ส่วน ELI5 ช่วยอธิบายความจริงนั้นให้คนแต่ละกลุ่มเข้าใจ**

อย่าใช้ ELI5 เพื่อเปลี่ยน Requirement, Decision, Scope หรือ Business Rule แบบเงียบ ๆ ถ้าระหว่างอธิบายแล้วพบ inconsistency หรือ missing decision จริง ให้ route กลับไปยัง BA phase ที่เกี่ยวข้องก่อน

---

# BA Discovery หยุดตรงไหน?

BA Discovery ตั้งใจอยู่ upstream ของ implementation

หน้าที่ของมันคือช่วยตอบว่า:

> **เรากำลังสร้างสิ่งที่ถูกต้อง ด้วยเหตุผลที่ถูกต้อง และอยู่ในขอบเขตที่ถูกต้องหรือยัง?**

เมื่อคำตอบนิ่งพอ ลักษณะของงานจะเปลี่ยนไป จาก Business Analysis ไปเป็น Engineering Discipline เช่น domain language, implementation seams, tickets, TDD, code review และ handoff ที่เชื่อถือได้ระหว่าง coding sessions

ตรงนี้คือจุดที่เหมาะจะไปต่อกับ [mattpocock/skills](https://github.com/mattpocock/skills)

Repository นี้ **ไม่ bundle หรือ copy Matt Pocock's skills** คุณติดตั้งแยกแล้วเลือกใช้เฉพาะส่วนที่เหมาะกับ Engineering Workflow ของคุณ

---

# ไปต่อกับ `mattpocock/skills`

Repo ของ Matt เด่นในฝั่ง Engineering หลังจาก Business Analysis ของเรานิ่งแล้ว Main engineering flow ปัจจุบันของเขาวางประมาณนี้:

```text
grill-with-docs
      ↓
   to-spec
      ↓
  to-tickets
      ↓
  implement
      ↓
 code-review
```

BA Discovery สามารถส่งงานเข้า flow นี้ได้ แต่ไม่จำเป็นต้องใช้ทุกขั้นทุกครั้ง

## Routing ที่แนะนำหลังได้ FRD

### 1. Technical assumptions ยังต้องถูก stress-test

ใช้ [`/grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)

เหมาะเมื่อ BA work จบแล้ว แต่ **engineering vocabulary, domain model, ADRs หรือ codebase-specific design** ยังควรถูก challenge กับ repository จริงอีกครั้ง

```text
BA Discovery
Business truth + approved FRD
        │
        ▼
grill-with-docs
Technical/domain stress-test ใน codebase จริง
```

ไม่จำเป็นต้องใช้เพียงเพราะมี FRD ถ้า technical decisions นิ่งแล้ว ให้ไปขั้นถัดไปได้เลย

### 2. Decision จบแล้ว และ Build จบได้ใน Session เดียว

ไป [`/implement`](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement) ได้โดยตรง

`implement` อยู่ downstream โดยตั้งใจ: มันเชื่อ upstream plan แล้วโฟกัสการเปลี่ยนสิ่งนั้นเป็น code ด้วย TDD, typechecking, tests, review และ commit

```text
BA Final FRD
    ↓
/implement
```

นี่คือเส้นทางสั้นสุดเมื่องานเล็กพอจะอยู่ใน fresh context เดียว

### 3. Decision จบแล้ว แต่ Build ต้องใช้หลาย Session

ใช้ [`/to-spec`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec) แล้วต่อด้วย [`/to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets) ก่อน `/implement` ทีละ ticket

```text
BA Final FRD
    ↓
/to-spec
    ↓
/to-tickets
    ↓
/implement   ← หนึ่ง tracer-bullet ticket ต่อ fresh session
    ↓
/code-review
```

`to-spec` ช่วยเก็บ settled engineering intent ให้รอดจาก context window ส่วน `to-tickets` แบ่ง spec ให้เป็น vertical, agent-ready units พร้อม blocking edges ที่ชัดเจน

### 4. Build ใหญ่หรือ technical path ยังไม่แน่นพอสำหรับ planning session เดียว

พิจารณา [`/wayfinder`](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder) ก่อน `to-spec`

เหมาะกับ engineering effort ขนาดใหญ่ที่ technical path เองยังต้องถูกแกะและตัดสินใจผ่านหลาย session

### 5. กำลังเปลี่ยน Agent, Session, Harness หรือ Working Directory

ใช้ [`/handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)

เหมาะมากตรง boundary ระหว่าง BA กับ implementation หรือทุกครั้งที่งานต้องถูกส่งต่อให้ Agent ใหม่

Handoff ที่ดีควร **ชี้ไปยัง durable artifacts แทนการ copy conversation ทั้งหมด** สำหรับ BA Discovery project โดยทั่วไปให้ชี้ไปที่:

```text
.ba/PROJECT.md
.ba/REQUIREMENTS.md
.ba/DECISIONS.md
latest approved phase snapshot
Final FRD
relevant engineering spec / ADRs
```

Agent ที่รับช่วงต่อควรเริ่มจาก artifacts เหล่านี้ ไม่ใช่จากการย่อทุกข้อความที่เคยคุยกัน

### 6. ไม่แน่ใจว่าควรใช้ Matt skill ตัวไหนต่อ

ใช้ [`/ask-matt`](https://github.com/mattpocock/skills/tree/main/skills/engineering/ask-matt)

มันเป็น router ของ engineering skills เหมือนที่ `/ask-ba` เป็น router ของ BA workflow ใน repo นี้

---

## Combined Workflow

สอง repository นี้รับผิดชอบคนละ layer ของ delivery problem เดียวกัน

```text
                         BUSINESS ANALYSIS

Idea / Pain / Existing System
            │
            ▼
        BA Discovery
            │
            ├── Background
            ├── Goal
            ├── Scope
            ├── Requirements
            ├── Decisions
            ├── System Design
            └── Final FRD
            │
            ▼
      "Are we building
       the right thing?"

──────────────────── ENGINEERING BOUNDARY ────────────────────

            │
            ▼
      mattpocock/skills
            │
            ├── grill-with-docs   optional technical stress-test
            ├── to-spec           preserve settled engineering intent
            ├── to-tickets        split multi-session work
            ├── implement         build with TDD
            ├── code-review       verify standards + spec
            └── handoff           cross agent/session boundaries
            │
            ▼
       Working Software
```

สรุปในประโยคเดียว:

> **BA Discovery ช่วยตัดสินใจว่าอะไรคือสิ่งที่ควรถูกสร้าง ส่วน `mattpocock/skills` ช่วยนำสิ่งนั้นไป engineer และ ship ให้ดี**

สอง repo มี overlap เท่าที่จำเป็นเพื่อเชื่อมงานต่อกัน แต่ไม่ได้พยายามแทนที่กัน

---

## Behavioral Confidence (v0.7)

BA Discovery เพิ่มชั้นทดสอบพฤติกรรมแบบ vendor-neutral สำหรับสิ่งที่ `ba-lint` ตรวจไม่ได้จาก state อย่างเดียว โดย `scripts/ba_eval.py` จะอ่าน normalized run record ร่วมกับ final `.ba/` state และ **ไม่เรียก model API เอง**

เป้าหมายคือจับหรือทำให้พฤติกรรมเหล่านี้มองเห็นได้ เช่น:

- ถาม Stakeholder ในเรื่องที่มีคำตอบอยู่ใน Project Evidence แล้ว,
- เปลี่ยนคำตอบที่ยังไม่แน่นอนให้กลายเป็น confirmed truth,
- ปลอม phase approval เมื่อตรงเข้า Design ด้วย external approved requirements,
- สร้าง Project Brain ใหม่แทนที่จะ resume จาก state เดิม,
- และแยก judgment เรื่อง Answerability / Question Pacing ไว้เป็น semantic review แทนการแกล้งทำว่า script ตัดสินได้แน่นอน

Scenario เดียวกันสามารถใช้กับ Claude Code, Codex, Gemini หรือ AI อื่นได้ เพียง normalize event ที่ platform เปิดเผยให้อยู่ใน schema กลาง Core contract จึงเป็น **vendor-neutral**

> **No vendor-specific feature is required for BA Discovery correctness.**

ดูวิธี manual capture, normalized events, result status และ optional adapters ได้ที่ [`evals/README.md`](evals/README.md) และดูตัวอย่าง **Brownfield** แบบครบชุดได้ที่ [`examples/brownfield-capacity-planner`](examples/brownfield-capacity-planner)


## ตัวอย่าง End-to-End ที่ใช้งานจริง

Repo นี้มี [ตัวอย่าง Project แบบครบชุด](examples/order-allocation-planner) ซึ่งรวม `.ba/`, approved snapshots ครบ 4 Phase และ Professional Report ที่ generate แล้ว


สมมติคุณมี Planning Application เก่า Planner ต้องใช้ SQL และ Excel ช่วยทำงาน และทุกคนมีความเห็นเกี่ยวกับระบบใหม่อยู่แล้ว

เริ่มด้วย:

```text
/ba-discovery:ba-discovery
พาเราไล่ตั้งแต่ problem, requirements และ system design ก่อน commit ไปที่ solution
```

BA Discovery inspect สิ่งที่มีอยู่ แยก facts ออกจาก assumptions ทำ Scope ให้ชัด และสร้าง approved FRD

ถ้า FRD บอก **what** ที่ระบบใหม่ต้องทำได้ชัดแล้ว แต่ codebase ยังต้อง sharpen ubiquitous language และ technical ADRs:

```text
/grill-with-docs
```

เมื่อ technical decisions นิ่งแล้วและ build มีขนาดใหญ่:

```text
/to-spec
/to-tickets
```

จากนั้นเริ่ม implementation session ใหม่จากหนึ่ง ticket:

```text
/implement #123
```

ถ้า ticket ถัดไปจะถูกทำโดย Agent อื่นหรือ Working Directory อื่น:

```text
/handoff
```

นี่คือความสัมพันธ์ที่เราตั้งใจ: **BA ก่อน → Engineering ต่อ → ใช้ durable artifacts เชื่อม boundary ระหว่างสองฝั่ง**

---

## Design Principles

BA Discovery ใช้หลักต่อไปนี้ตลอด Skill Suite:

- **Accuracy over speed.** Conclusion สำคัญต้อง trace กลับ evidence ได้
- **Do not reinvent the wheel.** ถ้ามี prior art, research หรือ solution ที่แข็งแรงอยู่แล้ว ให้ศึกษาก่อนสร้าง framework ใหม่
- **Ask the right source.** Stakeholder เป็นหนึ่งใน information sources ไม่ใช่ source เริ่มต้นของทุกคำถาม
- **Make questions answerable.** แปลง specialist choices ให้เป็นภาษา/สถานการณ์ที่ Stakeholder ตอบได้อย่างมีความหมาย
- **Conversation is not waste. Redundant conversation is waste.**
- **Do not fake completed phases.** External input ใช้ได้ แต่ provenance ต้องถูกเก็บตามจริง
- **Backtrack knowledge, not time.** ถ้าสิ่งที่พบภายหลังทำให้ assumption เดิม invalid ให้ revalidate เฉพาะ impact frontier และรักษางานส่วนที่ยัง valid
- **Project Brain is durable; the session is disposable.**

---

## Repository Layout

```text
ba-discovery/
├── .claude-plugin/
│   └── plugin.json
├── shared/
│   ├── contract-core.md
│   ├── contract-records.md
│   ├── contract-snapshots.md
│   └── question-contract.md
├── scripts/
│   ├── ba_lint.py
│   └── ba_eval.py
├── evals/
│   ├── behavior-contract.md
│   ├── schema/
│   ├── scenarios/
│   └── fixtures/
├── skills/
│   ├── ask-ba/
│   ├── ba-discovery/
│   ├── ba-understand/
│   ├── ba-requirements/
│   ├── ba-design/
│   ├── ba-spec/
│   └── ba-report/
├── examples/
│   ├── order-allocation-planner/
│   └── brownfield-capacity-planner/
├── tests/
├── CHANGELOG.md
├── VERSION
├── README.md
└── README.th.md
```

`.ba/` Project Brain เป็นของ Project ที่คุณกำลังวิเคราะห์ ไม่ใช่ของ Plugin Repository นี้

---

## Validate Repository

```bash
python tests/validate_repo.py
```

---

## Credits & Related Work

BA Discovery โฟกัส Business Analysis และ boundary ก่อน implementation โดยตั้งใจให้ compose กับ Engineering Workflow ที่ดี แทนที่จะพยายามครอบทุกอย่างเอง

สำหรับ Engineering continuation ที่อธิบายไว้ใน README นี้ ดู:

- [mattpocock/skills](https://github.com/mattpocock/skills)
- [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)
- [`to-spec`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec)
- [`to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets)
- [`implement`](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement)
- [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)

สำหรับการ re-explain approved project truth ให้เหมาะกับ audience เฉพาะกลุ่ม:

- [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)

Skill เหล่านี้ดูแลอยู่ใน repository ของผู้สร้างแต่ละรายและ **ไม่ได้ bundle อยู่ใน BA Discovery**

## ตรวจความสมบูรณ์เชิงโครงสร้าง (`ba-lint`)

BA Discovery ยังเป็นแบบ clone แล้วใช้ได้เลย หากเครื่องมี Python 3 จะสามารถใช้ `scripts/ba_lint.py` ที่พึ่งพาเฉพาะ standard library เพื่อตรวจโครงสร้าง `.ba/` แบบ deterministic เช่น ID ซ้ำ, reference ที่ชี้ไปหา record ที่ไม่มีอยู่, phase/lifecycle ที่ไม่ถูกต้อง, baseline ที่หาย, ชื่อ snapshot, approval block และ provenance ของการข้าม phase โดยไม่ต้อง `pip install` เพิ่ม

ถ้าไม่มี Python 3 งานสนทนาแบบ BA ยังทำต่อได้ แต่ต้องบอกตรง ๆ ว่า **deterministic lint was not run** และห้ามอ้างว่าได้ตรวจโครงสร้างแล้ว `ba-lint` ตรวจความสอดคล้องของโครงสร้าง ไม่ได้ให้คะแนนเชิงความหมายว่า requirement “ดี” หรือไม่
