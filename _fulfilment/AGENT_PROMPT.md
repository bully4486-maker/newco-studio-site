# Build a 5-page small-business website from an intake file

You are given one intake JSON file that has already passed the payment gate in `RUNBOOK.md`. Do not start from any other brief. Do not ask the client to visit, call, or meet.

Build a static site from the folder `template/` in this kit. The result is one pull request on a new per-client repository. Do not open that pull request against `newco-studio-site`.

The public pages you write must not mention agents, automation, or software writing the site. Write as the business, in UK English, using only the client's answers.

## Pages

Keep Home (`index.html`), Services, About and Contact. The intake field `fifth_page` is `gallery`, `faq` or `pricing`. Keep that one folder and delete the other two, including their links in every nav and in `sitemap.xml`.

`thanks.html` stays. It is what the enquiry form redirects to. It must not be linked in the nav.

## Copy

Use the client's words from these fields, and do not add facts they did not give:

- `business_name`, `what_you_do`, `services`, `area`, `tone`
- `home_offer` on the home page
- `about_facts` on the about page
- `contact_details` on the contact page
- `fifth_page_notes` on the fifth page
- `must_not_claim` is a ban list. Do not write those claims, and do not invent reviews, ratings, awards, years, prices, logos, or client names to fill a gap.

If a sentence would need a fact that is not in the intake, leave the sentence out. Do not write lorem, placeholder, demo, sample, or fictional-client text. Do not leave a `{{TOKEN}}` in the finished files.

You may break `services` into a list when the client separated items with line breaks. You may not add services they did not name.

Do not add a phone number, a home address, or a street address. The contact page shows the email they supplied in `contact_details`, plus the enquiry form. `area` is where their customers are, written as they wrote it. It is not a visit from us.

Tone follows `tone`. UK spelling. No exclamation marks used as a sales trick.

## Form and SEO

The contact form posts to `https://api.web3forms.com/submit` with `method="post"`. Set `access_key` to the client's own Web3Forms key, supplied with the task alongside the intake. Never use the studio site's key. Set the redirect to `thanks.html` with the correct relative path.

Each page needs a unique title and meta description written from the intake, `lang="en-GB"`, one `h1`, and `alt` on every image. Add JSON-LD `LocalBusiness` on the home page with the business name, the email they asked to publish, and `addressCountry` only if they said they are in the UK. Do not invent a street address. Include a sitemap with the five pages and a `robots.txt` that allows them.

## Images

Use an image only when `photo_notes` contains a URL the client supplied, or when image files were attached to the task by CoS from the client. Do not fetch stock photos of people. A page with no photo is correct.

## Look

Mobile first. System fonts. Text at least 16px. Body text width no wider than about 40rem. Buttons and links at least 44px tall. Contrast that would pass an accessibility check. A wrapping navigation is enough. Do not add cookies, local storage, session storage, or any analytics script.

The palette can follow the tone of the business. Do not copy the studio site's colours unless the client asked for them.

## Preview

Do not deploy to preview.newcopacks.co.uk and do not add a `CNAME` file. Follow the preview steps in `RUNBOOK.md`: a per-client `https://<owner>.github.io/<repository>/` URL, or `https://<project>.pages.dev` on the client's free Cloudflare Pages project. Put that URL in the pull request.

## Done

The pull request contains only the client site. Say which fifth page you kept, list any intake field you could not place because it was empty, and give the preview URL. Do not claim the site is finished if QA has not been run.
