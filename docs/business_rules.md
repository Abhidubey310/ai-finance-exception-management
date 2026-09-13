# Generic Business Rules

These rules are independently recreated for portfolio demonstration and are not derived from any employer's operating procedure.

## Classification hierarchy

The first valid rule determines the exception type:

1. Duplicate indicator = Yes → **Potential Duplicate**
2. Approval status is not Approved → **Approval Control**
3. Supporting documentation is incomplete → **Missing Documentation**
4. Reconciliation status is Unmatched or Partial → **Reconciliation Break**
5. Expected and actual amounts differ → **Amount Variance**
6. Description indicates mapping/master/data issue → **Data Quality**
7. Otherwise → **Other Exception**

## Severity model

- **Critical:** absolute variance of 50,000+; or 90+ days open; or high-value approval-control failure of 100,000+
- **High:** absolute variance of 10,000+; or 30+ days open; or potential duplicate of 10,000+
- **Medium:** absolute variance of 1,000+ or 10+ days open
- **Low:** all remaining cases

## Ownership

| Process area | Owner team |
|---|---|
| O2C | Revenue Operations |
| P2P | Accounts Payable |
| R2R | Financial Control |
| Intercompany | Intercompany Finance |
| Treasury | Treasury |

## Review controls

- Critical and High cases require explicit human approval.
- Potential duplicates and approval-control failures require explicit human approval regardless of severity.
- Critical cases and cases open for 60+ days are escalated.
- AI-generated text is advisory only and cannot replace the deterministic control classification.
- No automated transactional action is permitted in this portfolio implementation.

## Control principle

Finance controls should determine **what happened and whether a control broke**. AI can help explain the exception and prepare the investigation, but it should not manufacture evidence or make unsupported accounting decisions.