function Link({href="#",text="link", hoverColors=["bg-yellow-500","text-black"]}) {
	
	const stringHoverColors = hoverColors.map((i)=> `hover:${i}`).join(" ")	
	
	return (
		html`
			<a href="${href}" class="underline px-1 ${stringHoverColors}">${text}</a>
		`
	)
}