# communalspotify
A webapp for democratizing music in public spaces

## Building tailwindcss for dev:
just run `npm i` inside this folder, and it'll install the required packages.

And then run
```bash
$ npm run tcss:dev
```

## To build tailwind for production:
basically, the dev version of tailwind is pretty massive (2.26MB), but usually you don't need all of the classes provided to you by tailwind. So we have to purge the css of unused classes. 

To do this, run
```bash
$ npm run tcss:prod
```

> note: i've only tested this with bash. If you have problems with the npm script, basically just run `npm run tcss:dev` with the `NODE_ENV` environmental variable set to `production`. (although, i am using cross-env, so it should work)

PurgeCSS will look for tailwindcss classes in both `.html` and `.js` files inside of the `./templates` dir. [**Don't use string concatenation to create class names. Instead dynamically select a complete class name**](https://tailwindcss.com/docs/controlling-file-size#writing-purgeable-html)

You shouldn't ever build tailwind for production on your machine. It should be built into the production version when being uploaded to the server. (so, you can run `tcss:prod` as a build step basically)

