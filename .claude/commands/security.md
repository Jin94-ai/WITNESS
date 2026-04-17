보안 검사를 수행합니다.

대상: $ARGUMENTS

## 사전 확인 (Feedforward)

1. 대상 파일을 직접 읽어 실제 코드를 분석한다 (추정 금지)
2. 프레임워크와 언어를 파악해 관련 취약점 패턴에 집중한다
3. 민감 정보 파일(.env, config)이 있으면 커밋 이력도 확인한다

## 검사 항목 (OWASP Top 10)

1. **A01: Broken Access Control** — 인증/인가 검사
2. **A02: Cryptographic Failures** — 암호화 구현
3. **A03: Injection** — SQL, XSS, Command Injection
4. **A04: Insecure Design** — 설계 취약점, Rate Limiting 부재
5. **A05: Security Misconfiguration** — CORS, 헤더 설정
6. **A06: Vulnerable Components** — `npm audit` / `pip-audit` 실행
7. **A07: Authentication Failures** — 세션 관리, MFA
8. **A08: Data Integrity Failures** — 서명 검증
9. **A09: Security Logging Failures** — 인증 실패 로깅
10. **A10: SSRF** — 사용자 제공 URL 처리

## 추가 검사

- 민감 정보 노출 (.env, API 키 하드코딩)
- CORS 화이트리스트 범위
- Rate Limiting 구현

## 출력 형식

```markdown
# Security Audit Report

## Summary
- Critical: X개 | High: X개 | Medium: X개 | Low: X개

## Critical
- [파일:라인] [취약점명] [CWE-XXX]
  - 설명: ...
  - 수정 방안: (코드 예시 포함)

## High / Medium / Low
[동일 형식]

## Recommendations
1. [즉시 조치 항목]
2. [장기 개선 항목]
```

## 자가 체크 (Feedback)

- [ ] 모든 취약점에 실제 코드 위치(파일:라인)가 있는가?
- [ ] False positive를 제거했는가? (실제 악용 가능한 경우만)
- [ ] 수정 방안이 구체적인 코드 예시를 포함하는가?
- [ ] 보고서가 코드를 직접 수정하지 않고 제안만 하는가?
