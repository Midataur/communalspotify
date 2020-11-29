// Requires: Link

function DefaultHeader(){
	return (
		html`
			<div class="flex justify-between border-b-2 py-3 items-center">
				<h1 class="text-2xl font-bold">
					<a href="/" class=" hover:bg-yellow-500 hover:text-black pr-1">Shareify</a>
				</h1>
				
				<div class="flex ">
					<${Slot} name="headerNav">
						<div class="mr-3">
							<${Link} href="/join" text="Join Room" />
						</div>
						<div class="">
							<${Link} href="/create" text="Create Room" />
						</div>
					<//>
						
				</div>
			</div>
		`
	)
}
