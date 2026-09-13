# ASML Korea — Customer Support Engineer (CSE) 자기소개서

이병헌 / 경희대학교 응용물리학과 / lbh0391@khu.ac.kr
작성일 2026-09-04

핵심 소재: `optical-metrology-fitter` (TMM 기반 박막 광학 계측 역문제 파이프라인), KIST 양자광학 인턴 (SPDC·HOM 간섭)

> **붙여넣기 안내** — 문항 2·3은 자소서 입력창이 서식을 지원하지 않는 경우가 많아 마크다운 표 없이 평문으로 작성했습니다. 소제목의 `■` 기호는 그대로 붙여넣으셔도 되고, 불편하시면 지우고 줄바꿈만 남기셔도 무방합니다.

---

# 문항 1. [국문] 본인이 이해하고 있는 ASML CSE의 역할을 한 문장으로 표현해 주세요. 그렇게 생각한 이유와, 해당 역할을 커리어로 선택하는 데 가장 큰 영향을 준 요인을 구체적으로 작성해 주세요. (700자)

CSE는 고객의 라인에서 장비를 가장 먼저 마주하는 사람이고, 멈춤 1분이 수천 유로가 되는 시간 안에서 '진짜 원인'과 '그럴듯한 원인'을 갈라내는 사람이라고 이해했습니다.

KIST 현장실습에서 이렇게 생각하게 됐습니다. 광섬유 결합 효율이 유독 낮게 나온 적이 있습니다. 저는 당연히 정렬 문제라고 보고 처음부터 다시 잡았습니다. 회복되지 않았습니다. 한참을 그렇게 쓰고 나서야, 정렬을 고쳐도 안 된다는 것 자체가 원인이 거기 없다는 정보라는 걸 알았습니다.

그제야 커플러를 통과해 나오는 빛이 전보다 희미하다는 게 눈에 들어왔습니다. 손실이 그 구간에서 나고 있다는 뜻이었습니다. 위치를 좁힌 뒤 연구실 선배들과 공유했고, APC 파이버가 PC 커플러에 물려 있다는 것을 함께 확인했습니다. 두 규격은 끝면 연마 방식이 달라 체결은 되어도 밀착되지 않습니다. 증상은 광학적이었는데 원인은 부품 규격이었습니다.

Fab의 장비도 비슷하리라 봅니다. 로그와 센서는 언제나 그럴듯한 답을 하나 내놓습니다. 그것이 근본 원인인지 동반 현상인지 가르지 못하면 같은 알람이 되풀이됩니다. 다만 CSE가 그 판별을 하는 곳은 클린룸이고, 시간이 넉넉하지 않습니다. 저는 멈춘 장비를 다시 돌아가게 만드는 일이 이론을 푸는 것보다 재미있었고, 그래서 연구가 아닌 이 직무를 택했습니다.

---

# 문항 2. [국문 자기소개서] 지원 직무와 연관된 경험 및 전공 지식을 바탕으로 본인의 강점과 역량을 자유롭게 작성해 주세요. (제한 없음)

## ■ 왜 ASML인가

반도체 미세화의 상한을 정하는 공정은 리소그래피입니다. 해상도가 파장과 개구수로 정해지니, 더 작게 그리려면 광원을 짧은 파장으로 옮기거나 개구수를 키우는 수밖에 없습니다.

저는 2학년 때 반도체 공정 스터디 동아리에서 포토 공정 발표를 맡았습니다. HMDS 표면처리부터 PR 스핀코팅, 소프트 베이크, 노광, PEB, 현상, 하드 베이크까지 한 단계씩 정리했는데, 마지막 장이 ADI였습니다. 현상이 끝난 웨이퍼에서 CD와 오버레이를 측정해 다시 할지 말지를 판정하는 검사입니다.

준비하면서 패턴을 만드는 공정과 그 패턴이 제대로 만들어졌는지 판정하는 공정이 서로 다르다는 걸 알았습니다. 스핀코팅 회전속도나 베이크 온도를 아무리 잘 맞춰도, 결과를 재서 확인하지 않으면 공정은 자기가 잘하고 있는지조차 알 수 없습니다. 제 관심이 노광보다 계측 쪽으로 기운 것은 이 지점부터였습니다.

이후 학부 개인 연구로 박막 두께를 반사 스펙트럼에서 역산하는 계측 파이프라인을 다뤘고, 지금은 비선형광학 연구실에서 PPLN 소자의 설계 시뮬레이션을 하고 있습니다.

다만 이 물리가 수율로 바뀌는 자리는 연구실에 있지 않습니다. 고객사의 클린룸입니다. 저는 그쪽에서 일하고 싶습니다.

## ■ 제가 CSE에 적합하다고 보는 세 가지

1. 내가 만들지 않은 결과를 어디까지 믿을지 가려 본 **판정 역량**
2. 장비를 직접 제어하고, 멈췄을 때 되살려 본 **현장 경험**
3. 2년 8개월간 매주 사람의 질문을 받고 원인을 진단해 온 **응대 경험**

## ■ 첫째, 판정 — 내가 만들지 않은 결과를 어디까지 믿을 것인가

제 개인 계측 프로젝트는 AI 코딩 도구로 만들었습니다. 코드도 검증 스크립트도 제가 한 줄씩 짠 것이 아닙니다. 제가 한 일은 나온 결과를 읽고, 어디까지 믿어도 되는지 판단하고, 이 결과가 어디까지 유효한지를 정리하는 것이었습니다.

그 과정에서 오래 들여다본 것은 숫자보다 **검증의 구조**였습니다. 세 종류의 검증이 걸려 있었는데 증거력이 전부 달랐습니다.

무손실 구조에서 에너지가 보존되는지 보는 건 코딩 실수를 잡습니다. 물리 규약 자체가 틀린 경우는 못 잡습니다. Brewster 각에서 p편광 반사율이 소멸하는지, 반파장 박막이 광학적으로 존재하지 않는 것처럼 행동하는지, 이렇게 답을 이미 아는 상황과 대조해야 물리가 검증됩니다. 그런데 이 둘도 결국 자기 자신과의 일관성입니다. 세 번째는 같은 계산을 하는 다른 사람의 구현과 답을 맞춰 보는 것이었습니다. 무작위 조건 300개에서 반사율을 비교했을 때, 최대 차이가 소수점 15자리 아래였습니다. 물리적인 차이가 아니라 계산 순서가 달라 생긴 반올림입니다. 다만 이것도 완전히 독립적이지는 않습니다. 그 패키지를 만든 사람이 제 코드가 따른 논문의 저자이기 때문입니다. 같은 방법을 옳게 옮겼다는 것까지가 이 대조가 보증하는 전부입니다.

**이 셋의 증거력이 서로 다르다는 걸 구분하게 된 게 이 프로젝트에서 얻은 가장 큰 소득입니다.** 34개 항목이 전부 통과했다는 사실보다, 그중 무엇이 실제로 무엇을 보증하는지 아는 쪽이 중요했습니다.

이 경험이 제가 CSE에 지원하는 이유와 닿아 있습니다. **CSE는 자기가 설계하지 않은 장비가 내놓은 데이터를 보고 그것을 믿을지 판정하는 자리입니다.** 저는 그 판정을 소프트웨어를 상대로 먼저 해본 셈이고, "출력이 그럴듯하다"와 "출력이 옳다" 사이에 얼마나 많은 절차가 필요한지 배웠습니다.

전공 기반도 여기에 맞춰 쌓았습니다. 양자역학, 고체물리, 전자기학 1·2를 이수했고 반도체소자, 반도체 나노공정, 응집물질물리, 기계학습까지 모두 이수했습니다.

반도체소자에서 다룬 것은 공정 순서보다 소자의 물리였습니다. PN 접합의 공핍층과 내부 전위가 어떻게 정해지는지, 이상적 다이오드 방정식이 어떤 근사 위에 서 있는지, MOSFET에서 문턱전압이 무엇으로 결정되고 채널이 형성된 뒤 핀치오프를 지나 포화로 들어가는 과정이 물리적으로 무엇인지를 밴드 다이어그램으로 따라갔습니다. 금속-반도체 접합에서 쇼트키 장벽이 생기는 조건과 오믹 접촉이 되는 조건이 무엇으로 갈리는지, 이종접합에서 밴드 정렬이 어떻게 결정되는지도 함께 봤습니다. 공정 과목에서도 단계를 나열해 외우기보다 그 단계가 소자의 어떤 특성을 결정하는지로 연결해 이해하려 했습니다.

지금 비선형광학 연구실에서는 PPLN, 즉 주기적 분극반전 리튬나이오베이트 소자의 설계 시뮬레이션을 하고 있습니다. 이 소자는 분극 반전 주기가 위상정합 조건을 결정하기 때문에, 설계한 주기와 실제로 제작된 주기 사이의 작은 오차가 변환효율을 크게 떨어뜨립니다. 계산이 맞는 것과 소자가 동작하는 것이 별개라는 사실을 계측 프로젝트에서 한 번 봤는데, 이 연구실에서 다시 보고 있습니다.

## ■ 둘째, 경험 — 장비를 움직이고, 그 결과를 의심하는 법

KIST에서는 실험만 하지 않았습니다. 측정 자동화 코드도 직접 작성했습니다. Thorlabs Kinesis 모터 스테이지와 Swabian TimeTagger를 함께 제어해, 스테이지를 일정 간격으로 옮기며 각 위치에서 두 검출기의 단독 계수와 동시계수를 수집하는 코드였습니다. HOM dip을 얻으려면 광로차를 마이크로미터 단위로 훑어야 하는데 손으로는 재현성이 안 나옵니다.

이 코드에 의식적으로 넣은 두 가지가, 지금 보면 제가 장비를 대하는 방식을 그대로 보여줍니다.

**하나, 지령한 위치와 실제 위치를 따로 남겼습니다.** 스테이지에 이동 명령을 보내면 함수는 곧바로 반환됩니다. 명령이 접수된 것과 그 위치에 도착한 것은 별개입니다. 그래서 스테이지 상태를 폴링해 "이동 중"이 풀릴 때까지 기다리면서 그동안의 위치를 계속 읽어 별도 로그 파일로 남겼습니다. 측정 파일에는 제가 지시한 좌표가, 위치 로그에는 스테이지가 실제로 지나간 좌표가 같은 시각 태그로 쌍을 이뤄 저장됩니다. 로그를 열어 보면 이동 구간의 궤적과 멈춘 뒤 같은 값이 반복되는 구간이 그대로 남아 있습니다.

지시한 값과 실제로 일어난 일을 같은 칸에 적지 않는 것, 이게 제가 장비를 다루는 기본입니다.

**둘, 우연일치를 빼고 기록했습니다.** 동시계수 창을 τ로 두면 서로 무관한 두 광자도 확률적으로 같은 창에 들어옵니다. 그 배경은 R_A · R_B · τ 로 추정되므로, 각 측정점마다 이 값을 계산해 원시 동시계수에서 뺀 뒤 저장했습니다. 계수기 화면에 뜨는 숫자와 물리적으로 의미 있는 숫자가 다르다는 걸 코드 안에 적어 둔 셈입니다.

**앞서 쓴 APC/PC 커플러 건에도 남은 게 하나 더 있습니다.** 저는 이상 지점까지는 스스로 좁혔지만, 규격 불일치라는 결론은 선배들의 경험이 있어야 닿을 수 있었습니다. 어디까지가 제가 확인한 사실이고 어디부터가 도움이 필요한 부분인지 나눠서 공유한 것이, 혼자 오래 매달리는 것보다 결과적으로 빨랐습니다. 확인한 만큼과 확인하지 못한 만큼을 나눠서 말하는 습관은 여기서 얻었습니다.

계측 프로젝트에서는 같은 구도를 숫자로 봤습니다. 실제 시료의 SiO₂/Si 경계에는 1nm 정도의 중간층이 있는데 모델에는 그 층을 넣을 자리가 없었습니다. 그러자 피팅은 **그 어긋남을 옆에 있는 두께 값을 밀어서 흡수해 버렸습니다.** 두께가 0.745nm 부풀려진 것 자체는 물리적으로 당연합니다. 문제는 그것이 **이 파이프라인이 주장하던 정밀도의 168배**인데도, **잔차는 잡음의 1.5배로만 나빠져서 티가 나지 않았다**는 점입니다. 잘 맞는 것처럼 보이는 피팅이 답까지 맞다는 뜻은 아니라는 것을 여기서 봤습니다.

또 하나는, 조정으로 해결될 문제와 측정 조건 자체를 바꿔야 할 문제가 다르다는 것입니다. 단일 파장·단일 각도 반사율로는 박막 두께가 원리적으로 결정되지 않습니다. 한 주기 안에 해가 둘 생기고 그 패턴이 반복되어 차수도 정해지지 않습니다. 옵티마이저를 개선해서 될 일이 아니라 파장이나 각도를 늘려야 하는 일입니다. 현장에서 이 둘을 빨리 가르는 것이 다운타임을 좌우한다고 봅니다.

## ■ 셋째, 응대 — 상대가 말하는 증상과 실제 원인은 다릅니다

2023년 11월부터 2026년 6월까지 2년 8개월간 수학학원 조교로 일했습니다. 강의실과 분리된 인증실에서 학생 등하원 관리, 질문 응대와 오답 풀이, 채점, 교재 검사를 담당했습니다.

**학생이 막혔다고 말하는 지점과 실제로 무너진 지점은 거의 항상 달랐습니다.** 인수분해를 못 풀겠다고 가져오는데 무너진 곳은 분수 계산이고, 함수가 어렵다고 하는데 막힌 건 대입이라는 개념 자체입니다. 지목한 문제만 풀어주면 그 문제는 해결되지만 같은 유형이 다음 주에 다시 돌아옵니다.

그래서 질문을 받으면 먼저 어디까지 맞게 갔는지 확인하고, 처음 어긋난 지점을 찾아 거기서부터 다시 설명하는 방식으로 일했습니다. 시간은 더 걸리는데 같은 질문이 반복되지 않았습니다.

설명은 한 번 준비해서 끝나지 않았습니다. 같은 개념이라도 어떤 학생에게는 그림이, 어떤 학생에게는 수치 대입이, 어떤 학생에게는 왜 이 정의가 필요했는지가 통했습니다. 상대가 이해하지 못했다면 그건 상대의 문제가 아니라 제가 고른 설명 방식의 문제라고 여기며 일했습니다.

고객사마다 자주 발생하는 이슈와 원하는 대응 방식이 다르다고 들었습니다. 상대에 맞춰 설명을 다시 짜는 일을 2년 8개월간 매주 해 온 사람으로서, 그 조정은 감당할 수 있습니다.

## ■ CSE라는 직무의 조건에 대하여

ASML은 CSE를 "고객과 가장 먼저 접촉하는 사람", "문제가 생산에 영향을 주기 전에 감지하는 사람"으로 설명하고, 장비 한 대가 멈추면 분당 수천 유로의 비용이 발생한다고 밝히고 있습니다.

**이 일은 클린룸에서 합니다.** KIST에서 하루의 대부분은 계산이 아닌 조정이었습니다. 손끝의 힘 조절이 결과를 바꾸고, 어제와 오늘의 온도 차이가 데이터에 그대로 남는 환경을 겪었습니다. 가운을 입고 장비 앞에 서는 일이 낯선 노동이 아니며, 4일 근무 3일 휴무의 12시간 교대와 출장을 포함한 근무 조건도 인지하고 지원합니다.

**문제가 생산에 영향을 주기 전에 감지한다는 것.** 제 프로젝트에서 같은 구조를 봤습니다. 반사율의 두께 민감도가 반주기마다 0이 되는 지점에서 계측기는 국소적으로 눈이 멉니다. 두께가 변해도 신호가 변하지 않으니 장비는 정상값을 보고합니다. 405nm에서는 이 사각지대가 68.9nm 간격으로 반복됩니다. 예방적 감지란 결국 우리 장비가 어디에서 눈이 머는지 미리 아는 일이라고 봅니다.

**기록.** CSE 업무에는 서비스 리포트 작성이 포함됩니다. 저는 프로젝트에서 잘 나온 결과만 남기지 않았습니다. 실패한 시도와, 이 결과를 인용하기 전에 읽어야 할 한계를 함께 남겨 뒀습니다. 리포트는 다음 사람이 같은 문제를 처음부터 겪지 않게 하는 장치라고 생각합니다.

**침착함.** 이건 아직 충분히 증명하지 못했습니다. 분당 수천 유로가 걸린 상황을 겪어본 적이 없습니다. 다만 침착함이 성격이 아니라 절차에서 나온다는 것은 압니다. 무엇부터 배제할지 정해진 순서를 갖고 있으면 서두르지 않아도 빠릅니다. 실험실에서도, 시험 기간의 학원에서도 저를 지탱한 건 그 순서였습니다.

## ■ 제가 부족한 부분

광학과 계측의 원리는 알지만 EUV 스캐너의 서브시스템 구성, 진공 시스템과 메카트로닉스, ASML의 서비스 절차와 진단 도구는 모릅니다. 이 간극은 문헌으로 메울 수 없고 현장에서만 메울 수 있습니다. 또 근거가 갖춰질 때까지 판단을 미루는 경향이 있는데, 고객의 장비가 멈춰 있는 상황에서는 불완전한 정보로 결정해야 합니다. 이에 대해서는 "지금 확실한 것 / 강하게 추정되는 것 / 아직 확인되지 않은 것"을 분리해 보고하는 방식을 원칙으로 삼으려 합니다.

## ■ 맺으며

제 배경은 노광이 아니라 계측입니다. 이것이 CSE 지원자로서 제가 가진 가장 뚜렷한 차이라고 봅니다. 장비가 낸 결과를 데이터로 판정할 수 있다는 건, 고객이 수율 문제를 들고 왔을 때 그것이 장비 이슈인지 공정 조건인지 구분해 설명할 수 있다는 뜻이기 때문입니다.

입사 후에는 담당 모듈에서 발생한 알람과 추정 원인, 실제 조치, 재발 여부를 스스로 색인화해 기록하고 팀과 공유하겠습니다. 계측 프로젝트의 결과를 다른 사람의 구현체와 대조해 봐야 비로소 믿을 수 있었던 것과 같은 이유입니다.

---

# 문항 3. [영문 자기소개서] 위 국문 자기소개서를 기반으로 본인에 대한 자기소개를 영문으로 작성해 주세요. (제한 없음)

## Why ASML

The process that sets the ceiling on semiconductor miniaturisation is lithography: resolution follows from wavelength and numerical aperture, so drawing smaller means a shorter source wavelength or a larger aperture.

In my second year I presented the photo process for a study group — HMDS priming, resist spin-coating, soft bake, exposure, post-exposure bake, develop, hard bake — and the last slide was ADI: measuring CD and overlay on the developed wafer to decide on rework.

Preparing that talk taught me something. **Making the pattern and judging whether it was made correctly are separate processes.** However carefully you set a spin speed or a bake temperature, without measuring the result the line cannot know how it is doing. That is where my interest moved to metrology.

Since then I have worked on a pipeline that recovers thin-film thickness from a reflectance spectrum, and I now run design simulations for periodically poled lithium niobate. But the place where that physics turns into yield is not a laboratory; it is a customer's cleanroom.

## Three Reasons I Fit This Role

1. **Judgement** — I worked out how far to trust results I did not produce myself.
2. **Experience** — I drove the instrument myself, and brought it back when it stopped.
3. **Communication** — for two years and eight months I took people's questions weekly and diagnosed what was actually wrong.

## Judgement — How Far to Trust Output I Did Not Produce

Let me be direct: my metrology project was built with AI coding tools. I wrote neither the code nor the validation scripts line by line. What I did was read the output, decide how far it could be trusted, and set out where its validity ends.

What I spent longest on was not the numbers but **the structure of the validation**, because the three kinds in place did not carry equal weight. Energy conservation catches coding mistakes, not a wrong physical convention. Cases whose answers are known in advance — reflectance vanishing at the Brewster angle, a half-wave film behaving as if optically absent — are what test the physics. And both are still only self-consistency. The third check compared answers against someone else's implementation of the same calculation: across 300 random configurations the largest difference in reflectance fell below the fifteenth decimal place: rounding from a different order of operations, not a difference in physics. Even that is not fully independent, since its author wrote the paper my code follows, so it establishes only that the method was transcribed correctly.

**Learning to separate those three is what I took from the project.** That all thirty-four checks passed matters less than knowing which guarantees what — and a CSE, too, looks at data from equipment they did not design and decides whether to believe it.

My coursework backs this: quantum mechanics, solid state physics, electromagnetism I and II, Semiconductor Devices, Semiconductor Nanofabrication, Condensed Matter Physics and Machine Learning, all completed. Semiconductor Devices gave me device physics rather than a process sequence — how a PN junction's depletion region and built-in potential are set, which approximations the ideal diode equation rests on, what determines a MOSFET's threshold voltage and what pinch-off and saturation physically are, and what separates a Schottky barrier from an ohmic contact.

In the laboratory, a PPLN device's poling period sets its phase-matching condition, so a small discrepancy between the designed and fabricated period collapses the conversion efficiency — a calculation being correct and a device working are different statements.

## Experience — Driving an Instrument, and Doubting What It Reports

At KIST I did not only run the experiment by hand; I wrote the measurement automation myself — a Thorlabs Kinesis stage driven with a Swabian TimeTagger, stepping the path difference while collecting singles and coincidence counts, because a Hong–Ou–Mandel dip must be swept at micrometre resolution and by hand is not reproducible. Two things I built into that code say how I treat equipment.

**First, I logged the commanded position and the actual position separately.** Sending a stage a move command returns immediately; the command being accepted and the stage having arrived are different things. So I polled the stage's status until "moving" cleared, reading its position throughout into a log of its own. The measurement file holds the coordinates I asked for; the position log holds the coordinates the stage actually passed through, paired under the same timestamp. **Not writing the instruction and what actually happened into the same column** is my basic posture toward instruments.

**Second, I subtracted accidental coincidences before recording.** With a coincidence window τ, unrelated photons still fall into the same window at about R_A·R_B·τ. I computed that background at every point and subtracted it, writing into the code that the number a counter displays and the number that means something physically are not the same.

**And once the cause was not the alignment.** Coupling efficiency came out unusually low; I took it for an alignment problem and spent a long time redoing it without recovery. **That failure was itself information**: if fixing the alignment does not help, alignment is not the cause.

What I then noticed was that the light coming through the coupler was dimmer than it had been — the loss was happening in that section. Having located it, I shared what I had with the senior researchers and together we confirmed it: **an APC fibre had been mated into a PC coupler.** An APC ferrule is polished at 8° and a PC one is flat, so the two connect mechanically but their endfaces cannot meet, leaving an air gap and an angular mismatch that costs exactly that light.

Two things stayed with me. **An optical symptom does not mean an optical cause**: low coupling efficiency makes you reach for the alignment, and that day it was a part specification. And separating what I had confirmed from what I had not is a habit I took from that day.

I saw the same shape in numbers in my metrology project. A real SiO₂/Si boundary carries an interfacial layer about 1 nm thick, and my model had no place to put it. The fit therefore **absorbed the mismatch by pushing the one parameter it did have** — the film thickness — inflating it by 0.745 nm. That much is physically unsurprising. What matters is that the shift was **168× the precision this pipeline claimed**, and yet **the residual worsened by only 1.5× the noise**, so nothing announced it. A fit that looks good is not the same as an answer that is right.

The other thing is that a problem adjustment can settle and a problem that requires changing the measurement itself are different. A single-wavelength, single-angle reflectance measurement cannot determine a film thickness even in principle — two solutions arise within one period, and the pattern repeats so the order is undetermined as well. No optimiser fixes that; more wavelengths or more angles do. Telling those two apart quickly is what determines downtime in the field.

## Communication — The Symptom and the Cause Are Not the Same

For two years and eight months I worked as an assistant at a mathematics academy — managing arrivals and departures, answering questions, working through wrong answers, and marking.

What I confirmed week after week is that **the place someone says they are stuck and the place they actually broke down are almost never the same.** A student brings a factorisation problem when what collapsed was fraction arithmetic; solving the one they pointed at fixes that one, and the type returns the following week.

So I established how far they had gone correctly, found the first step that went wrong, and re-explained from there. It took longer, and the question stopped coming back. An explanation is never prepared once, and when someone did not understand, I treated that as a fact about the explanation I had chosen, not about them.

## What This Role Actually Demands

ASML describes the CSE as "the first contact with the customer" and someone who "detects problems before they can impact production," and notes that a machine down costs thousands of euros per minute.

**This work happens in a cleanroom, not at a desk.** At KIST most of a day was adjustment rather than calculation — where the pressure of a fingertip changes the result and yesterday's temperature is still visible in today's data. Standing at an instrument in a gown is not unfamiliar work, and I apply knowing that shift work and travel are part of the role.

**Detecting problems before they reach production.** I saw this in my project: the thickness sensitivity falls to zero every half period, and there the instrument is locally blind — the thickness can change while the signal does not, so the tool reports a healthy value. At 405 nm that blind spot recurs every 68.9 nm. Preventive detection means knowing where your instrument cannot see: no alarm and no problem are not the same statement.

## Where I Fall Short

I understand optics and metrology, but not EUV scanner subsystems, vacuum hardware, or ASML's service procedures — a gap that closes only in the field. I have never worked with thousands of euros a minute at stake either, and I tend to defer a judgement until the evidence is complete. Composure comes from procedure, not temperament: my principle under time pressure is to report in three registers — certain now, strongly inferred, still unverified.

## Closing

My background is measurement rather than exposure, and that is my clearest difference as a candidate: judging a tool's output as data means being able to tell a customer whether a yield problem is the machine or the process.

Once in the role, I will keep an indexed record of alarms raised, causes suspected, actions taken and whether they recurred, and share it with my team. Individual experience disappears unless it is left behind.

---

# 부록 — 면접 대비

## ⚠ 가장 먼저 준비할 것: "이 프로젝트 직접 하셨나요?"

**반드시 나옵니다.** 자소서에 AI 도구 활용을 명시했으므로 오히려 물어보기 쉬워집니다. 준비된 답:

> "코드도 검증 스크립트도 AI 도구로 만들었습니다. 제가 한 일은 나온 결과를 어디까지 믿을지 판단하는 것이었습니다. 검증이 세 층으로 걸려 있었는데 증거력이 서로 달랐습니다. 에너지 보존은 코딩 실수만 잡고, Brewster 각처럼 답을 이미 아는 상황과의 대조라야 물리를 검증하며, 그마저도 결국 자기 일관성입니다. 가장 강한 건 다른 사람 구현과의 대조였습니다. tmm 패키지와 랜덤 스택 300개를 비교해 최대 편차가 9.3e-15, 배정밀도 반올림 수준이었습니다. 다만 그 패키지 저자가 제 코드가 따른 논문의 저자라서 완전히 독립적이진 않습니다. 방법을 옳게 옮겼다는 것까지만 보증됩니다."

이렇게 답하면 그 다음 질문이 **"그럼 Brewster 각이 왜 그렇게 되는지 설명해보세요"**로 이어집니다. 아래 목록이 D-day까지 반드시 채워야 할 최소 방어선입니다.

## 마감까지 공부할 순서 (우선순위대로)

**1순위 — 4pm vs 1.3nm (자소서 핵심, 반드시)**
같은 모델로 데이터를 만들고 같은 모델로 피팅하면 모델 형태 오차가 구조적으로 보이지 않습니다(inverse crime). 4pm은 그 조건에서 나온 랜덤 오차 하한(CRLB)이고, 1.3nm는 계면층·거칠기 등 모델이 놓친 것을 넣었을 때의 편향입니다. **핵심: 랜덤 오차와 계통 오차는 별개의 예산이고, 후자가 300배 크다.**

**2순위 — 왜 단일 파장으로는 두께를 못 재는가**
투명 박막에서 R ≈ A + B·cos(2δ), δ = (2π/λ)·n·d·cosθ. 주기함수이므로 (a) 한 주기 안에서 오르내려 같은 R에 두 개의 d가 대응하고(flank), (b) λ/2n 주기로 반복되어 차수가 안 정해집니다(order). 전자는 위상 정보(타원편광), 후자는 광대역/각도 스캔으로만 해소. **옵티마이저 문제가 아님.**

**3순위 — χ²가 좋은데 답이 틀리는 경우**
1nm 계면층을 무시했을 때 잔차 RMS = 3.07e-4 (노이즈 σ_R = 2e-4의 약 1.5배). 같은 조건에서 두께 편향은 0.745nm = 랜덤 오차(4.44pm)의 168배. **즉 잔차는 1.5배, 답은 168배.** 이 비대칭이 요점입니다.
- ⚠️ "잔차가 멀쩡했다"고 말하지 마십시오. 251점에서 χ² 검정을 하면 1.5배는 걸립니다. 정확한 주장은 "적합도가 나빠지는 폭과 답이 틀어지는 폭이 비례하지 않는다"입니다.
- ⚠️ exp04 스크립트의 요약 출력 줄은 루프 마지막 값(t_int=3nm의 1.6e-3)을 찍습니다. 1nm 조건의 값은 표에 있는 3.067e-04입니다. 숫자를 인용할 때 표를 보십시오.

**4순위 — Brewster 각 (유도 10분이면 됩니다)**
$r_p = 0$ 조건은 $n_2\cos\theta_i = n_1\cos\theta_t$. Snell 법칙과 연립하면 $\theta_B = \arctan(n_2/n_1)$. **물리적 의미**: 반사파 방향과 투과 매질 내 쌍극자 진동 방향이 나란해지는데, 쌍극자는 자기 진동축 방향으로 복사하지 않으므로 p편광 반사가 사라집니다. 흡수 매질(k≠0)에서는 완전히 0이 되지 않고 최소값만 가지며, **그 최소값이 k의 크기를 반영한다는 것이 타원편광의 물리적 근거**입니다.

**5순위 — 분기 규칙**
$e^{-i\omega t}$ 규약 + $\tilde n = n+ik$이면 +z 진행파는 $e^{i\mathrm{Re}(k_z)z}e^{-\mathrm{Im}(k_z)z}$. 물리적 감쇠를 위해 $\mathrm{Im}(k_z)\ge 0$. 반대 근을 고르면 거리에 따라 커지는 비물리적 파가 되고, 두꺼운 흡수층에서 $e^{ik_zd}$가 오버플로합니다.

## 인용 가능한 수치

| 항목 | 수치 |
|---|---|
| 알고리즘 노이즈 플로어 | 4 pm (CRLB 대비 MC 효율 1.019) |
| 현실적 정확도 (RSS) | 1.33 nm |
| 검증 통과 | 34 / 34 |
| 외부 교차검증 오차 | max ΔR = 9.3e-15 (p편광 R), 300개 랜덤 스택, 시드 20260815. 대조 상대는 `tmm` 0.2.0 (S. J. Byrnes) — **논문 저자와 동일인이므로 독립성은 절반**. 참조 패키지 미설치 시 Tier C가 스킵되어 29/34만 돕니다 |
| 벡터화 가속 | 162× (425 ms → 2.62 ms) ※ exp01_results.json 실측. README의 195.8×는 다른 실행 결과이니 JSON 값을 쓰십시오 |
| 사전탐색 효과 | 3/9 → 9/9 성공 |
| 축퇴 후보 / 주기 | 8개 / 137.82 nm (이론 137.79) |
| 각도 캘리브레이션 | 0.1° → 0.147 nm |
| 계면 산화층 전달계수 | 0.75 nm / nm |
| 거칠기 전달계수 | 0.438 nm / nm |
| 계측기 사각지대 | 405 nm에서 68.9 nm 간격 |

## 그 밖의 예상 질문

- **"AI로 만든 걸 왜 자소서에 썼나요?"** → 숨기면 면접에서 드러나고, 무엇보다 제가 강점으로 내세우는 것이 코드 작성이 아니라 검증이기 때문입니다. CSE도 자기가 만들지 않은 장비의 출력을 판정하는 자리라고 이해했습니다.
- **"이 프로젝트에서 가장 아쉬운 점은?"** → 실측 검증입니다. 공개 타원편광 데이터로 시도했으나 단일 균일층 모델의 한계로 실패했고, 다음 단계는 층을 여러 sub-layer로 나눈 구배 굴절률 모델입니다.
- **"CSE에 물리 전공이 왜 필요한가?"** → 로그가 주는 것은 상관관계이고, 어떤 상관관계가 인과일 수 있는지 좁히는 것은 장비의 물리입니다.
- **"KIST에서 가장 어려웠던 것은?"** → (직접 겪으신 일이므로 자신 있게. HOM dip visibility, 정렬 재현성, 적분 시간 등 실제 기억을 쓰십시오.)

## 스테이지 자동화 관련 예상 질문 (직접 하신 일이라 강하게 답하십시오)

- **"왜 지령 위치와 실제 위치를 따로 저장했나요?"** → `move_to`는 명령만 보내고 즉시 반환합니다. 명령이 접수된 것과 그 위치에 도착한 것은 다릅니다. HOM dip은 광로차에 마이크로미터 단위로 민감해서 x축이 어긋나면 dip 위치와 폭이 통째로 왜곡되므로, 상태를 폴링해 "이동 중"이 풀릴 때까지 기다리며 그동안의 위치를 로깅했습니다. **주의**: 기록되는 것은 이동 중 궤적입니다. 로그를 보면 값이 변하다가 멈춘 뒤 같은 값이 4~5개씩 반복되는 구간이 나오는데, 그게 정착 구간입니다. (백래시를 정량적으로 측정한 것은 아니므로 그렇게 말하지 마십시오.)
- **"우연일치 보정 공식은?"** → 두 검출기의 단독 계수율을 $R_A$, $R_B$, 동시계수 창을 $\tau$라 하면 무관한 광자쌍이 같은 창에 들어올 기대율은 $R_A R_B \tau$입니다. 실제 코드에서 $\tau$ = 500 ps로 두고 매 측정점에서 이 값을 빼고 저장했습니다.
- **"왜 자동화가 필요했나요?"** → 재현성입니다. 손으로 스테이지를 돌리면 스텝 간격이 일정하지 않고, 각 위치의 적분 시간도 달라집니다. dip visibility를 정량적으로 비교하려면 조건이 같아야 합니다.
- **"APC/PC 문제는 어떻게 찾았나요?"** → 처음에는 저도 정렬 문제로 알고 한참 다시 잡았습니다. 회복되지 않는다는 것 자체가 원인이 정렬이 아니라는 신호였고, 그 다음에 커플러를 통과해 나오는 빛이 전보다 희미하다는 것을 눈으로 확인했습니다. 손실이 커플러 구간에서 발생하고 있다는 뜻이었습니다. 위치를 특정한 뒤 선배들과 공유해 APC 파이버가 PC 커플러에 물려 있다는 것을 확인했습니다.
- **"왜 APC를 PC에 물리면 안 되나요?"** → APC는 페룰 끝면이 8도로 비스듬히, PC는 평면으로 연마돼 있습니다. 체결은 되지만 끝면이 밀착되지 못해 공기 간극과 각도 불일치가 남고, 그 경계에서 굴절로 빠져나가는 빛이 손실이 됩니다. 뒤반사도 함께 늘어납니다. 관례상 APC는 녹색, PC/UPC는 파란색 커넥터로 구분합니다.
- **"혼자 해결한 게 아니지 않나요?"** → 이상 지점까지는 스스로 좁혔고, 규격 불일치라는 결론은 선배들의 경험이 있어야 닿을 수 있었습니다. 저는 이것이 잘못된 진행이었다고 생각하지 않습니다. 확인한 사실과 도움이 필요한 부분을 나눠서 공유하는 편이 혼자 오래 매달리는 것보다 빨랐습니다.
- **"TimeTagger의 input delay는 왜 설정했나요?"** → 두 검출기까지의 케이블 길이와 검출기 자체의 지연이 달라, 물리적으로 동시인 사건이 타임태거에서는 어긋나 도착합니다. 그 차이를 보정해야 동시계수 창 안에 들어옵니다.

## 포토 공정 발표 (2024.10) — 실제 다룬 내용, 그대로 답하시면 됩니다

발표 순서: Concept → PR(positive/negative) → Wafer Prime(HMDS) → PR Spin-Coating → Soft Bake → Exposure(contact/proximity/projection) → PEB → Develop → Hard Bake → ADI

- **"HMDS는 왜 쓰나요?"** → 실리콘 표면이 친수성이라 PR과 접착이 안 됩니다. HMDS로 소수성 표면으로 바꿔 접착력을 확보합니다.
- **"PEB는 왜 하나요?"** → 노광 시 웨이퍼에서 반사된 빛과 입사광이 간섭해 PR 내부에 정재파가 생기고, 그 결과 PR 측벽이 물결 모양이 됩니다. 100도 근처에서 수십 초 열처리해 확산으로 이 주름을 완화합니다.
- **"Soft bake와 Hard bake의 차이는?"** → 소프트 베이크는 용매를 부분 증발시켜 접착력을 올리는 단계, 하드 베이크는 더 높은 온도(120도 수준)에서 용매를 완전히 제거해 후속 공정을 견디게 하는 단계입니다.
- **"스핀코팅에서 중요한 변수는?"** → 회전속도가 PR 두께와 균일도를 결정합니다. 가장자리에 두껍게 맺히는 edge bead는 따로 제거해야 합니다.
- **"ADI가 무엇인가요?"** (⭐ 자소서의 핵심 연결고리) → 현상까지 끝난 뒤 CD와 오버레이를 측정하는 검사입니다. 아직 식각 전이라 기준을 벗어나면 PR을 벗기고 다시 할 수 있습니다. **패턴을 만드는 공정과 그것이 제대로 만들어졌는지 판정하는 공정이 분리되어 있다는 것**을 여기서 알았고, 제 관심이 계측으로 간 출발점입니다.
- **"노광 방식 세 가지의 차이는?"** → contact는 마스크를 웨이퍼에 붙여 해상도는 좋지만 마스크가 손상되고 오염됩니다. proximity는 간격을 두어 손상은 줄지만 회절로 해상도가 나빠집니다. projection은 렌즈로 마스크 상을 축소 투영해 마스크 수명과 해상도를 함께 얻습니다.

---

# 문항 4. [기타 대내외 경험] 수상경험 / 프로젝트 / 공모전 / 대회 / 연구 및 기타 대내외 경험을 자유롭게 기재해 주세요. (3,000자)

■ 수상 및 장학

운해장학재단 제13기 장학생 / 2026.02
- 외부 장학재단 선발.

교내 성적우수 장학생 / 2025학년도 1학기, 2학기, 2026학년도 2학기
- 3개 학기 선발.

■ 연구 경험

비선형광학 연구실 학부연구생 / 2025.12 ~ 현재
- 양자광학 실험 및 이론, PPLN(주기적 분극반전 리튬나이오베이트) 설계 시뮬레이션 수행. 졸업논문 진행 중.
- PPLN은 분극 반전 주기가 위상정합 조건을 결정하는 소자입니다. 설계 주기와 실제 제작된 주기 사이의 작은 오차가 변환효율을 크게 떨어뜨리기 때문에, 이 연구실에서 배우고 있는 것은 결국 "설계값과 실물 사이의 간극을 어떻게 다룰 것인가"입니다. 계산이 맞는 것과 소자가 동작하는 것은 다른 문제라는 사실을 여기서 배웠습니다.

KIST 한국과학기술연구원 단기 현장실습 / 2025.06 ~ 2025.08
- 광학 테이블에서 실험을 직접 구상해 마이컬슨 간섭계, SPDC 광원, HOM 간섭 순서로 단계적으로 구축.
- 측정 자동화 코드를 직접 작성했습니다. Thorlabs 모터 스테이지와 Swabian TimeTagger를 함께 제어해 광로차를 훑으며 단독 계수와 동시계수를 수집하는 코드로, 지령 위치와 실제 도달 위치를 따로 로깅하고 우연일치 배경을 보정해 저장하도록 만들었습니다.
- 앞 단계의 정렬이 어긋나 있으면 다음 단계는 아예 신호가 나오지 않기 때문에, 문제가 생겼을 때 어디까지가 확실한지를 뒤에서부터 되짚어 확인하는 습관이 생겼습니다.

개인 연구 프로젝트 — 박막 광학 계측 파이프라인 (전달행렬법 기반)
- 반사 스펙트럼에서 박막 두께를 역산하는 계측 파이프라인. 코드는 AI 코딩 도구로 만들었고, 제가 한 일은 나온 결과를 어디까지 믿을 수 있는지 판단하고 그 유효 범위를 정리하는 것이었습니다.
- 검증이 세 층(에너지 보존 / 해석적 극한 / 외부 독립 구현체 대조)으로 걸려 있었는데, 증거력이 서로 다르다는 점을 구분하게 된 것이 가장 큰 소득이었습니다. 외부 구현체와의 최대 편차는 1e-14 수준이었습니다.
- 잘 나온 결과만 남기지 않았습니다. 실패한 시도와, 이 결과를 인용하기 전에 읽어야 할 한계 7가지를 함께 남겨 두었습니다.

■ 교내 활동

학과 학술동아리 KHYPHY 부회장 / 2026.01 ~ 현재
- 40여 명 규모 전공 학습 동아리에서 회장을 보조하며 세미나와 개강총회 등 행사를 기획, 운영.

반도체 공정 스터디 동아리 VANS 부원 / 2024.09 ~ 2024.12
- 포토 공정 발표 담당 (2024.10). HMDS 표면처리, PR 스핀코팅, 소프트 베이크, 노광(contact/proximity/projection), PEB, 현상, 하드 베이크, ADI까지 전 단계를 정리.
- 마지막 단계인 ADI에서 CD와 오버레이를 재서 rework 여부를 판정한다는 것을 알게 됐습니다. 제 관심이 계측으로 기운 출발점입니다.

■ 대외 활동

AWS 주관 글로벌 기업 연계 AI 역량 강화 프로그램 / 2026.08.28 ~ 08.29
- 생성형 AI 및 클라우드 기초 학습 후, 팀 프로젝트로 헤어 스타일과 헤어샵 추천 서비스, 헤어 모델과 미용사 매칭 서비스를 기획, 구현, 발표.
- 이메일 인증 로그인과 네이버 API, Gemini API 연동까지 실제 동작하는 수준으로 완성했습니다. 외부 API 연동에서는 문서에 적힌 응답과 실제 응답이 다르고 에러 메시지가 원인을 알려주지 않습니다. 결국 로그로 구간을 좁혀 들어가는 것 말고는 방법이 없었습니다.

■ 아르바이트

엠코드 수학학원 조교 / 2023.11 ~ 2026.06 (2년 8개월)
- 강의실과 분리된 인증실에서 학생 등하원 관리, 질문 응대와 오답 풀이, 채점, 교재 검사 및 교재 타이핑 보조.
- 가장 오래 한 일이고 CSE 지원에 가장 직접적으로 닿아 있습니다. 질문을 받다 보면 학생이 막혔다고 말하는 지점과 실제로 무너진 지점이 다른 경우가 대부분이었습니다. 인수분해를 못 풀겠다고 가져오지만 무너진 곳은 분수 계산입니다. 지목한 문제만 풀어주면 같은 유형이 다음 주에 다시 돌아오므로, 저는 어디까지 맞게 갔는지를 먼저 확인하고 처음 어긋난 지점부터 다시 설명하는 방식으로 일했습니다.
- 같은 개념이라도 통하는 설명이 학생마다 달랐습니다. 그림이 통하는 학생, 수치 대입이 통하는 학생, 왜 이 정의가 필요했는지를 말해줘야 통하는 학생이 따로 있었습니다.
- 2년 8개월간 한자리를 지키며 시험 기간의 몰림과 비수기의 편차를 반복해서 겪었습니다.

■ 정리

수상이나 공모전으로 내세울 것은 많지 않습니다. 다만 위의 경험들이 향하는 데는 대체로 같습니다. 눈에 보이는 증상을 그대로 처치하지 않고 처음 어긋난 지점을 찾는 일입니다. 학원에서는 학생의 오답이, 실험실에서는 회복되지 않던 결합 효율이, 계측 프로젝트에서는 멀쩡해 보이는 잔차 뒤에 숨은 편향이 그 대상이었습니다.
