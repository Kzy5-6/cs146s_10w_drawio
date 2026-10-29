## Experimental Hypotheses

- **H1 — Structural reliability:** Contract and schema prompting will produce more outputs that pass JSON, schema, and graph checks than brief prompting.
- **H2 — Semantic fidelity:** Contract prompting will preserve more case-specific business steps, branches, and loops than schema prompting.
- **H3 — Schema constraint effect:** Explicitly supplying the JSON Schema through Ollama's `format` parameter will improve or maintain structural validity compared with the previous schema-mode prompt.

## Check Definitions

- **JSON validity:** The raw output can be parsed as JSON after removing any surrounding Markdown code fences.
- **Schema validity:** The parsed JSON satisfies the required structure and field types defined in `spec.schema.json`.
- **Graph validity:** Node IDs are unique and do not use reserved values; every edge references existing source and target nodes.
- **Semantic fidelity (manual review):** The output preserves the case's required steps, decision branches, loops, and business rules without unsupported additions.
- **Ambiguity handling (manual review):** The output identifies missing, ambiguous, or conflicting requirements and raises appropriate questions instead of silently inventing a resolution.
### Dev Round 1 Results

We evaluated 24 generations across four dev cases, three prompting modes, and two repetitions per mode.

- **Brief:** 5/8 valid JSON outputs, 0/8 schema-valid outputs, and 3/8 graph-valid outputs.
- **Contract:** 8/8 valid JSON outputs, 8/8 schema-valid outputs, and 8/8 graph-valid outputs.
- **Schema:** 8/8 valid JSON outputs, 8/8 schema-valid outputs, and 8/8 graph-valid outputs.

**Observation:** Brief prompting performed substantially worse than contract and schema prompting on automated structural checks. Contract and schema prompting tied on these eight dev records. Automated checks do not establish semantic correctness, so manual review is still required.

**Iteration plan:** Preserve the brief baseline and investigate whether explicitly including the JSON Schema in the schema-mode prompt, along with setting temperature to 0, improves consistency. Re-run the affected dev experiments and compare the results before evaluating on the held-out eval split.

### Dev Round 2: Schema Prompt and Temperature Update

**Changes made:**
- Added the JSON Schema text to the schema-mode prompt.
- Set `temperature=0` for all prompting modes.
- Applied the schema constraint through the `format` parameter only in schema mode.

**Results:** 24 generations across four dev cases, three prompting modes, and two repetitions per mode.

| Mode | Valid JSON | Schema-valid | Graph-valid |
|---|---:|---:|---:|
| Brief | 6/8 | 0/8 | 1/8 |
| Contract | 8/8 | 8/8 | 8/8 |
| Schema | 8/8 | 8/8 | 8/8 |

**Comparison with Round 1:** Brief improved from 5/8 to 6/8 valid JSON outputs, but graph validity decreased from 3/8 to 1/8. Contract and schema remained at 8/8 on all three automated checks. The changes did not demonstrate a measurable structural-validity improvement for schema mode on this dev sample.

**Next step:** Review the failed brief outputs and manually inspect semantic correctness before running the held-out eval split. The eval phase has since been completed; results are reported below.
### Brief Mode Failure Analysis

Review of Round 2 brief outputs identified recurring structural failures:

- Some outputs used `from` and `to` instead of the required `source` and `target` edge fields.
- Some outputs omitted the required `questions` property.
- Some outputs used unexpected top-level structures or field names, such as `process` or Chinese field names.
- Some outputs were not valid JSON.

These failures explain why valid-looking JSON did not necessarily pass schema or graph validation. Contract and schema modes passed all automated structural checks in both dev rounds, so further prompting changes should be justified by semantic review rather than structural scores alone.

**Decision:** Keep the contract and schema implementations as comparison baselines, and inspect semantic correctness and uncertainty handling alongside automated checks. The held-out eval split has since been run. Do not treat automated structural validity as proof that the generated workflow is correct.

### Manual Semantic Review: D1

- **Contract, repeat 1:** Preserved the three business steps: receiving a return, quality inspection, and inventory registration. It also raised a relevant question about handling failed inspections.
- **Contract, repeat 2:** Preserved the same three steps, but its questions were more generic.
- **Schema, repeat 1:** Passed automated structural checks but replaced the actual business workflow with generic start, process, and end nodes.
- **Schema, repeat 2:** Passed automated structural checks but used generic steps rather than the specific return-processing workflow.

**Finding:** Schema validity did not guarantee semantic completeness. For D1, contract outputs were more faithful to the case than schema outputs in this sample. This is a qualitative observation based on two repetitions, not a statistically conclusive result.

### Manual Semantic Review: D2

- **Contract, repeat 1:** Preserved the application workflow: student submits an application, an administrator reviews it, and the application either proceeds to notification or is returned for revision. It also raised relevant questions about approval criteria and notification channels.
- **Contract, repeat 2:** Preserved the same main steps and approval/rejection branches, but included only one question.
- **Schema, repeats 1 and 2:** Produced structurally valid, identical generic workflows using start, step1, step2, and end nodes. Neither output captured the student application and administrator review process.

**Finding:** For D2, contract prompting preserved the case-specific workflow better than schema prompting in these two repetitions. The schema outputs demonstrate that structural validity alone does not establish semantic completeness. This is a qualitative observation based on two repetitions, not a statistically conclusive result.

### Manual Semantic Review: D3

- **Contract, repeat 1:** Preserved the order and inventory-check decision. It included both the in-stock branch leading to shipping and the out-of-stock branch leading to handling the shortage, but the shortage-handling details remained unspecified.
- **Contract, repeat 2:** Preserved order receipt, inventory checking, and the in-stock shipping branch. It included the out-of-stock branch but omitted a follow-up handling node.
- **Schema, repeats 1 and 2:** Produced identical generic workflows with start, step1, step2, and end nodes. Neither output represented order processing or inventory decisions.

**Finding:** Contract prompting retained substantially more case-specific logic than schema prompting in these repetitions. However, even the contract outputs left the out-of-stock procedure unresolved, showing that a structurally valid workflow may still be incomplete. This is a qualitative observation based on two repetitions, not a statistically conclusive result.

### Manual Semantic Review: D4

- **Contract, repeat 1:** Included confirmation before review, a review step, a confirmation step, and confirmation after review. However, the relationships and labels were vague, and the questions were somewhat repetitive.
- **Contract, repeat 2:** Generated a different workflow involving input, process initiation, steps A and B, conflict detection, and conclusion output. It was more detailed but differed substantially from repeat 1, so its fidelity to the original case requires careful review.
- **Schema, repeats 1 and 2:** Produced identical generic workflows with start, step1, step2, and end nodes, without preserving case-specific details.

**Finding:** Contract outputs varied substantially between repetitions, while schema outputs were consistent but generic. Consistency and structural validity alone do not establish semantic fidelity. This is a qualitative observation based on two repetitions, not a statistically conclusive result.

## Dev Phase: Overall Findings

### Structural Validity

Across both dev rounds, contract and schema prompting achieved 8/8 valid outputs in each round according to the automated checks. Brief prompting performed less reliably, with failures including invalid JSON, missing required fields, unexpected top-level structures, and incorrect edge field names.

### Semantic Fidelity

Manual review of D1–D4 showed that schema outputs frequently passed structural validation while replacing case-specific workflows with generic start, step, and end nodes. Contract outputs generally preserved more business details, such as review decisions, inventory branches, and return processing, but could still omit steps or vary substantially between repetitions.

### Prompting Iteration

The schema-mode prompt was updated to include the JSON Schema, and temperature was set to 0 for all modes. The second dev round did not demonstrate a measurable structural-validity improvement for schema mode because its automated results were already perfect in the first round. Brief-mode results varied between rounds.

### Limitations and Next Steps

These findings are based on four dev cases and two repetitions per case and mode, so they should be treated as preliminary observations rather than statistically conclusive results. Automated checks assess JSON, schema, and graph structure, while semantic fidelity requires manual review. The held-out eval cases have now been run; the results and manual review are reported below.

### Eval Phase: Overall Structural Results

The eval phase included 24 generations: four eval cases, three prompting modes, and two repetitions per mode and case.

| Prompting mode | JSON valid | Schema valid | Graph valid |
|---|---:|---:|---:|
| Brief | 7/8 | 7/8 | 7/8 |
| Contract | 6/8 | 5/8 | 5/8 |
| Schema | 8/8 | 8/8 | 8/8 |

The improved evaluation run completed 24 generations across four evaluation cases, three prompting modes, and two repetitions per mode and case. Schema mode achieved 8/8 passes for JSON validity, schema validity, and graph validity. Brief mode achieved 7/8 passes on all three checks, while contract mode achieved 6/8 JSON-valid outputs and 5/8 schema-valid and graph-valid outputs.

These results suggest that schema-constrained generation was the most reliable approach for structural validity in this evaluation run. However, automated structural checks do not establish semantic fidelity. The generated diagrams still require manual inspection to verify that they preserve case-specific steps, branches, loops, and business rules.




### Manual Semantic Review: E1

- **Brief, repeats 1 and 2:** Both outputs passed JSON, schema, and graph checks. They included visitor registration, collecting a pass, returning the pass, and leaving.
- **Contract, repeat 1:** Preserved visitor registration, pass collection, pass return, and departure. Its questions raised plausible issues about pass validity, return-time recording, and exception handling.
- **Contract, repeat 2:** Preserved the same main steps, but used generic edge labels and asked more general questions.
- **Schema, repeats 1 and 2:** Both outputs passed structural checks but replaced the visitor process with generic start/process/end or start/step/end nodes. Their questions were also generic and did not address visitor registration or pass handling.

**Finding:** Brief and contract outputs both preserved the core visitor-pass workflow in this sample. Schema outputs passed structural checks but were generic and omitted the case-specific process. This is a qualitative observation based on two repetitions, not a statistically conclusive result.

### Manual Semantic Review: E2

- **Brief, repeat 1:** The output was malformed JSON and failed all automated checks.
- **Brief, repeat 2:** The output passed all automated checks and represented upload, format checking, and an error/re-upload path, but the error/re-upload node was not connected back to upload, so the retry loop was incomplete.
- **Contract, repeats 1 and 2:** Both preserved upload, format checking, and the error/re-upload loop returning to the upload step.
- **Schema, repeats 1 and 2:** Both outputs passed structural checks but generated the same generic start/process/end workflow. Neither represented file-format validation, the error branch, or the re-upload loop.

**Finding:** Contract prompting best preserved the intended retry loop in these repetitions. Brief prompting was inconsistent: one output failed structurally, while the other passed structural checks but did not close the retry loop. Schema outputs passed structural checks but omitted the case-specific workflow. This illustrates that structural validation alone does not establish that branching and looping behavior is correct.

### Manual Semantic Review: E3

- **Brief, repeats 1 and 2:** Both outputs passed all automated checks and preserved staff review, passing the item to “him” for approval, and notifying the applicant. Both asked who “him” refers to.
- **Contract, repeat 1:** Preserved staff review, approval by the unspecified person, and applicant notification. It explicitly asked who “he” refers to and noted that the approval rules were unclear.
- **Contract, repeat 2:** The output was malformed JSON and failed all automated checks.
- **Schema, repeats 1 and 2:** Both outputs passed structural checks but produced identical generic start/process/end workflows. They did not preserve the review, approval, notification, or ambiguous reference.

**Finding:** Brief outputs preserved the key steps and explicitly surfaced the ambiguous pronoun. One contract output did the same, while its second repetition failed JSON parsing. Schema outputs passed structural checks but omitted the case-specific workflow. These are qualitative observations based on two repetitions, not statistically conclusive results.

### Manual Semantic Review: E4

- **Brief, repeats 1 and 2:** Both outputs passed all automated checks and preserved the conflict between the 1000-yuan supervisor-approval rule and the 800-yuan direct-payment rule. They asked how amounts between 800 and 1000 yuan should be handled, but did not resolve the ambiguity.
- **Contract, repeat 1:** The JSON parsed, but the output omitted the required `questions` property and used `from`/`to` rather than `source`/`target`, so schema and graph checks failed.
- **Contract, repeat 2:** The output was empty after approximately 3,212 seconds and failed all automated checks.
- **Schema, repeats 1 and 2:** Both outputs passed structural checks but produced generic start/process/end workflows. They omitted the monetary thresholds and the conflict between the approval and payment rules.

**Finding:** Brief prompting best preserved the conflicting thresholds and surfaced the unresolved 800–1000 yuan boundary. The contract outputs were unreliable in this case: one failed the required structure and the other returned no output. Schema outputs passed structural checks but omitted the thresholds and conflict. This demonstrates the need to assess rule consistency and decision-boundary behavior in addition to automated structural checks.
### Brief Prompt Improvement

In the initial v3 development run, the brief mode passed JSON validation in 4/8 outputs, schema validation in 0/8, and graph validation in 2/8. Inspection showed that the model sometimes used alternative field names such as `name` and `type`, or returned a different top-level structure.

I revised the brief prompt to explicitly require the `nodes`, `edges`, and `questions` fields, specify the required fields within nodes and edges, and prohibit Markdown code fences and alternative field names.

In the follow-up development run, brief mode passed JSON, schema, and graph validation in 8/8 outputs. Contract and schema modes also passed all three checks in 8/8 outputs each. This result supports the hypothesis that clearer structural instructions improve output-format compliance in this small test set. Automated validation does not establish semantic correctness, which still requires manual review.
## Final Conclusion

Across the latest eval run, schema mode achieved 8/8 passes on JSON, schema, and graph checks; brief mode achieved 7/8 on each check; and contract mode achieved 6/8 JSON-valid outputs and 5/8 schema-valid and graph-valid outputs. Therefore, the hypothesis that contract and schema prompting would both outperform brief prompting was only partly supported on eval: schema prompting was most structurally reliable, while contract prompting had notable failures on E3 and E4.

The dev experiments showed that the initial brief prompt was structurally unreliable. After it was revised to explicitly require `nodes`, `edges`, and `questions`, with the required `id`/`label`, `source`/`target`/`label` fields and no alternative field names or Markdown fences, the follow-up dev run achieved 8/8 on all three checks for brief, contract, and schema modes. This supports the value of explicit structural instructions in the small dev sample, though the run metadata still labels the changed prompt as `v3`, so the version label does not distinguish the before-and-after prompt text.

Manual review showed that structural validity and semantic fidelity are different. Contract outputs often preserved case-specific steps and branches, including the E2 retry loop and E3 approval ambiguity, but contract reliability was uneven in eval. Brief outputs preserved important details in E1, E3, and E4, but the E2 retry loop was incomplete in one passing output and the other E2 output was malformed. Schema outputs were structurally consistent but often reduced the cases to generic start/process/end workflows, omitting key business rules. E4 also showed why ambiguity checks matter: the conflict between 800-yuan direct payment and 1000-yuan supervisor approval was identified by brief prompting but not resolved.

Overall, the evidence supports using automated JSON/schema/graph checks together with manual review of business steps, branches, loops, and unresolved requirements. Results are preliminary because each split contains only four cases and two repetitions per mode. The experiment also has a reproducibility limitation: the brief prompt was changed after the initial v3 run without updating the recorded `prompt_version` label.
