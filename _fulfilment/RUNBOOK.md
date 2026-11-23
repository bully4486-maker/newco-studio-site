# £299 website fulfilment

This folder is not published. GitHub Pages builds the studio site with Jekyll, and Jekyll does not publish a folder whose name starts with an underscore. `_config.yml` also lists `_fulfilment` under `exclude`. Do not add a `.nojekyll` file to the studio repository root. That file would turn Jekyll off and this folder would go live.

The live order log is not this folder's `orders.csv`. That file is a header template only. The working log lives outside the repository at `/workspace/pivot/orders.csv`. Override the path with `--orders` or the `NEWCO_ORDERS_CSV` environment variable. Never commit a row from a real order.

Public pages must not mention agents, automation, or software writing the sites. This runbook is internal.

## Who does what

1. The enquiry form on `/website-299/` emails the intake fields through Web3Forms. The field names match `intake.schema.json`.
2. CoS saves that submission as one JSON file. `intake.example.json` shows the shape. It is not a customer.
3. CoS drafts the quote by running the generator below. Keith does not draft it.
4. CoS fills the three bank tokens privately in the copy that is sent, then emails the quote. The filled bank details are never committed.
5. Keith's only manual step is confirming that the deposit has cleared. He tells CoS. CoS then sets the two payment cells in the private log. Nobody starts a build from Keith's word alone, and Keith does not run the build.
6. CoS runs the guard. Only a pass may start a build.
7. One cloud agent runs from `AGENT_PROMPT.md` and the intake JSON, on a copy of `template/`.
8. QA runs on the built folder. A failure is fixed once (the second run, which is also the revision run if the client has not yet seen a preview). A second QA failure stops the order.
9. CoS sends the client the preview URL. There is one revision round after that, still inside the two-run cap.
10. After sign-off, the balance of £149.50 is due. Keith confirms it has cleared. CoS records that in the private log, then hands the site over.

## Draft the quote

```bash
python3 _fulfilment/generate_quote.py path/to/intake.json -o /secure/NCS-299-20261123.html
```

Optional flags: `--invoice-number NCS-299-20261123`, `--date YYYY-MM-DD`, `--due YYYY-MM-DD`. The due date defaults to seven days after the invoice date and applies to the £149.50 deposit. The £149.50 balance is due on sign-off.

Open the HTML and use the browser's print dialogue to save a PDF if you want one.

Before sending, replace only these three tokens in the private copy:

- `{{BANK_ACCOUNT_NAME}}`
- `{{BANK_SORT_CODE}}`
- `{{BANK_ACCOUNT_NUMBER}}`

Leave them braced in git. Do not put a trader address, a home address, or a phone number on the quote. The signature is "Keith Bullock, trading as NewCo Studio" with keith@newcopacks.co.uk.

## Private orders log

Copy the header from `orders.csv` into `/workspace/pivot/orders.csv` if that file does not already exist, and keep the working file off git.

```text
order_id,business_name,payment_cleared,payment_cleared_by,agent_runs,run_dates,qa_fails,status,preview_url
```

- `payment_cleared` stays blank, or any value other than `cleared`, until Keith confirms the deposit has arrived.
- CoS then sets `payment_cleared` to `cleared` and `payment_cleared_by` to `CoS`. Both cells are required. A "yes" from anyone else does not open the gate.
- `agent_runs` is how many cloud-agent runs this order has already had. Dates of those runs go in `run_dates`, separated by semicolons (`2026-11-24;2026-11-26`).
- `qa_fails` is how many times QA has failed.
- `preview_url` is the per-client HTTPS URL from the section below, once it exists.

After a run, CoS updates `agent_runs`, `run_dates`, `qa_fails`, `status` and `preview_url` in the private log before another run is considered.

## Gate

Run this against the private log, not against the header template. If you omit `--orders`, the guard reads `$NEWCO_ORDERS_CSV` or `/workspace/pivot/orders.csv`:

```bash
python3 _fulfilment/guard.py --order-id NCS-299-20261123 --usage-percent 42
# or, to override the default path:
python3 _fulfilment/guard.py --orders /workspace/pivot/orders.csv --order-id NCS-299-20261123 --usage-percent 42
```

`--usage-percent` is the percentage of the Cursor usage allowance already used, read from the Cursor usage meter before the run. The guard refuses when the figure is omitted.

The guard refuses, and no build starts, when any of these is true:

- `payment_cleared` is not `cleared`, or `payment_cleared_by` is not `CoS`
- this order already has 2 agent runs
- 3 agent runs are already logged today across every order
- Cursor usage is at or above 80%
- this order has 2 QA failures

On a refusal, stop. If the reason is usage, tell Keith via CoS and stop every order, not only this one. If the reason is two QA failures, escalate that order to CoS and do not start a third run.

## Build

1. Copy `_fulfilment/template/` to a working directory outside the studio site.
2. Put the intake JSON beside it.
3. Start the cloud agent with `AGENT_PROMPT.md` and that JSON. One run produces one pull request on the client repository.
4. The agent deletes the two fifth-page folders the client did not choose, so the site is Home, Services, About, Contact, and one of Gallery, FAQ or Pricing.

## QA

```bash
python3 _fulfilment/qa.py /path/to/built-site
python3 _fulfilment/qa.py --lighthouse /path/to/built-site
```

QA fails when HTML checks fail, an internal link is broken, a `{{token}}` remains, visible text contains lorem, placeholder, demo, sample, or fictional-client, or the enquiry form is not a Web3Forms POST with the client's own access key.

`--lighthouse` runs a mobile performance check when Chrome and Lighthouse can run, and fails below 90. If they cannot run, that one check is skipped and the rest still count. Two QA failures on an order stop the work.

Do not point QA at `template/`. The template still contains tokens on purpose.

## Preview URLs

Do not use https://preview.newcopacks.co.uk. Its certificate does not match the hostname, plain HTTP returns 500, and the preview repository's github.io address 301-redirects to that custom domain because a CNAME is set. Do not change DNS.

Give the client a free per-client HTTPS URL instead.

### GitHub Pages on the default github.io URL

1. Create a new repository for this client. Put it on the client's GitHub account when they have one. Until handover it may sit on an account you control, still as its own repository.
2. Do not add a file named `CNAME`. Do not set a custom domain under Settings, Pages.
3. Push the built site to the default branch, including the `.nojekyll` file from the template, so Pages serves the HTML as files.
4. Settings, Pages, Build and deployment: Deploy from a branch, the default branch, folder `/ (root)`.
5. Wait until the deployment is green. The preview URL is `https://<owner>.github.io/<repository>/` for a project site, or `https://<owner>.github.io/` only when the repository itself is named `<owner>.github.io`.
6. Open that https URL yourself. It is covered by GitHub's certificate for `*.github.io`. Send that URL. Do not send a `http://` link, and do not send preview.newcopacks.co.uk.

### Cloudflare Pages on the default pages.dev URL

1. Use the client's own Cloudflare account, on the free plan. Create a Pages project from their repository, or use Direct Upload of the built folder.
2. Do not add a custom domain. Do not attach preview.newcopacks.co.uk.
3. Cloudflare shows `https://<project>.pages.dev`. That hostname is on Cloudflare's certificate. Send that URL.
4. The client attaches their own domain later, on their account, after the balance has cleared.

### The existing preview repository

This change is not made in `newco-studio-site`. The repository whose Pages custom domain is `preview.newcopacks.co.uk` should have its `CNAME` file deleted, and the custom domain cleared in that repository's Pages settings, so its `*.github.io` URL is served directly over HTTPS. This studio repository's `CNAME` is `studio.newcopacks.co.uk` and stays as it is. No DNS records are edited.

## Handover

After the client signs off and Keith confirms the £149.50 balance has cleared:

1. CoS records the balance in the private log.
2. Deploy the signed-off files to the client's own Cloudflare Pages or GitHub Pages account, under their domain, or send a zip if that is what they chose on the form.
3. Email a short delivery note: the live URL, where the files are, that one revision round was included, and that they own the account, the domain and the files. There is no ongoing fee.
4. Do not keep the only copy of the site on our side.

## Checks you can run without an order

```bash
python3 _fulfilment/generate_quote.py --self-test
python3 _fulfilment/guard.py --self-test
python3 _fulfilment/qa.py --self-test
```
