// loaded spacer
// Spacer, written by darcy in 2020.

function Spacer({text}){
	
	if (text!=null) {
		return html`
			<div class="flex items-center my-4">
				<div class="flex-grow h-px bg-white"></div>
				<div class="px-2">${text}</div>
				<div class="flex-grow h-px bg-white"></div>
			</div>
		`
	} else {
		return html`
			<div class="flex items-center my-4">
				<div class="flex-grow h-px bg-white"></div>
			</div>
		`
	}

}

