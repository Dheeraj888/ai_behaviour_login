# How to Produce Real Evaluation Numbers

The current app returns **training accuracy** after model training. For your report, do not invent test accuracy or confusion-matrix numbers.

A stronger evaluation procedure is:
1. Collect at least 15-20 normal samples.
2. Keep several samples aside as legitimate test data.
3. Ask another person to attempt the same login interaction to collect real impostor/anomalous test samples (do not share your real password; use a demo account/password).
4. Evaluate predictions on these held-out samples.
5. Record TP, TN, FP, FN and calculate accuracy.

If you do not perform a separate holdout test, explicitly write that the shown metric is training accuracy and list this as a limitation.
