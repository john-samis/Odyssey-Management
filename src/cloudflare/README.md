# Cloudflare Pages redirect

Publish `src/cloudflare/pages` as a Cloudflare Pages static site. The site intentionally has no backend behavior.

`pages/_redirects` is the only operational file: replace its Google Forms URL once when the permanent attendance Form is created. The `/form` path can then remain unchanged indefinitely, including on printed QR codes.

The attendance report job does not depend on Cloudflare Pages and Cloudflare Pages does not need access to Google or GCP credentials.
