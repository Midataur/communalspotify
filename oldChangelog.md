# new changelog style:
just do git commits with this template:
```
<type>(scope): <subject>
```

example:
```
fix(styles): padding on buttons

feat(templates): use base template for join.html
```

possible types are [commitizen](https://github.com/commitizen/cz-cli) standard.

![types](https://github.com/commitizen/cz-cli/raw/master/meta/screenshots/add-commit.png)

uses [git-chglog](https://github.com/git-chglog/git-chglog) to generate changelogs.

---

# old stuff

**Current:**
* `added` search api (max)
* `added` 404 page (darcy)
* `changed` preactBase to reference the Header component (darcy)
* `added` Header and Link components (darcy)
* `changed` room template to use the preactBase (darcy)
* `added` debug route so that we can test stuff (darcy)
* `added` _defineProperty function to make doing public field declarations work, and also, getting it to work on more browsers (darcy)
* `added` components system and functions (darcy)
* `added` notes on how to properly use js and preact (darcy)
* `added` preactBase.html template (darcy)
* `changed` create.html and index.html templates to have tailwind and nicer styles. (darcy)
* `added` docs for how to build and get setup with tailwind. (darcy)
* `added` styles.css and tailwind config (darcy)
* `added` package.json (darcy)
* `changed` contents of .gitignore to include node modules and editor configs (darcy)
* `added` base.html template (darcy)
* `added` design .sketch files (darcy)
* `added` initial mvp (max)

**Terms:**
* added — the creation of something
* changed — the changing of something
* removed — getting rid of something
* fixed
* *note*: there may be some overlap with the terms (eg. adding a function, but changing a file). In these cases use the one you feel most appropriate.

**Format:**
```
`added/changed/removed/fixed` ... (name)
```
