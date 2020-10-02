# communalspotify
A webapp for democratizing music in public spaces

## Preact and javascript:
So, we are using [preact](https://preactjs.com) for this project, as it allows us to do fun reactivity stuff pretty easily. and is much smaller than react + react-dom.

In order to use preact, create a template with this:

```js
{%extends "preactBase.html" %}
{%block title%}title | Shareify{%endblock%}
{%block code %}

{%endblock%}
```

And you're done, you've made a template using preact!

Now to change the default contents:

`preactBase.html` has the variables `header` and `main` already declared. Those are our two components. 

Just add code that redefines the `header` and/or `main` components, and preact will render that component instead of the default. 

Instead of using JSX as the html language inside our js code, we use [htm](https://github.com/developit/htm) which is quite small, and has great integration with preact. To use it, just make a tagged template literal with `html`.

```js
main = html`<p>oooh, html </p>`
```

> Think of template literals like python's f-strings. where instead of using `{}` to include code, you use `${}`.

**eg:**
```js
{%extends "preactBase.html" %}
{%block title%}A simple demo (clock) | Shareify{%endblock%}
{%block code %}

class Clock extends Component {

  constructor() {
	super();
	this.state = { time: Date.now() };
  }

  // Lifecycle: Called whenever our component is created
  componentDidMount() {
	// update time every second
	this.timer = setInterval(() => {
	  this.setState({ time: Date.now() });
	}, 1000);
  }

  // Lifecycle: Called just before our component will be destroyed
  componentWillUnmount() {
	// stop when not renderable
	clearInterval(this.timer);
  }

  render() {
	let time = new Date(this.state.time).toLocaleTimeString();
	return html`<span>${time}</span>`;
  }
}

main = html`<${Clock}/>`

{%endblock%}
```

This demo just displays the current time. 

**Note:**

because we are using the "module" type script tag, you have to make sure that you write correct js. That means declaring your variables, y'all. for more info about some best practices, [click here](https://github.com/airbnb/javascript). 

In regards to variables: use `const/let` instead of `var`, as `const` and `let` are block scope, whereas `var` is function-scoped (ie. global). 

### `_defineProperty()`

`_defineProperty()` is a nice little helper function to let us define properties in browsers that dont support public field declarations. This is literally just copied from a babel build. 

**How to use:**


```js
// instead of:
class Hello extends Component {
	state = {
		value:""	
	}
	
	onInput = (ev) => {
		this.setState({
			value: ev.target.value
		})
	}
	
	onSubmit = (ev) => {
		ev.preventDefault()
		
		this.setState({
			name:this.state.value
		})
	}
	
	render() {}
}

// write:
class Hello extends Component {
	constructor() {
		super()
		
		_defineProperty(this, "state", {
			value: ""
		})
		
		_defineProperty(this, "onInput", (ev) => {
			this.setState({
				value: ev.target.value
			})
		})
		
		_defineProperty(this, "onSubmit", (ev) => {
			ev.preventDefault()
			
			this.setState({
				name: this.state.value
			})
		})
	
	}

	render() {}
}

// you might also be able to write:
class Hello extends Component {
	constructor() {
		super()
		this.state = {
			value: ""
		}
		
		this.onInput = (ev) => {
			this.setState({
				value: ev.target.value
			})
		}
		
		this.onSubmit = (ev) => {
			ev.preventDefault()
		
			this.setState({
				name: this.state.value
			})
		}
	
	}
	render() {}
}

// but i need to check if that works cross-browser. Babel doesnt try to convert the above code, so, uhh, ┐(￣ヘ￣)┌,  
```

basically, from what i can tell, doing public fields as in the first example just adds them to the class using the [`defineProperty` function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Public_class_fields#Public_static_fields). So the custom function basically just reimplements the default js behaviour, which makes sense, because it's babel.

## Preact Components:
all components live inside the `components` directory, under individual js files. 

for information on how to make them, [have a look here](https://preactjs.com/guide/v10/components)

to import a component, add this to the top of the `code` block:

```
{{component_import("Spacer", "WhateverTheFileNameIs", ...)}}
```

The component name in js should be the same as the filename excluding the extension, not because it affects anything, just because it's nicer.


### A list of our components:

| name | props | description |
|------|-------|-------------|
| `Spacer` | `{text}` | takes `text` and puts it in between two lines. adds y padding. If it can't find `text`, just displays a line. |


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

