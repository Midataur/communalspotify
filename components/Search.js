// Requires: useKeyPress

function Search() {

    const [isSearchOpen, setIsSearchOpen] = useState(false)

    const openSearchUI = () => { setIsSearchOpen(true) }
    const closeSearchUI = () => { setIsSearchOpen(false) }
    
    if (!isSearchOpen) return html`
        <button onClick=${openSearchUI}>open search</button>
    `
    
    
    const escPress = useKeyPress('Escape');
    const [value, setValue] = useState("")
    const [searchResults, setSearchResults] = useState(false)
    
    if (escPress) closeSearchUI()
    
    const onSubmit = e => {
        fetch(`/api/search?q=${value}&roomcode=${roomCode}&limit=10`)
            .then(r => r.json())
            .then(data => setSearchResults(data.tracks))
            .catch(() => {error:"fetching search results failed"})
            
        console.log("component/Search", "Submitted form")
        e.preventDefault()
    }
    
    const onInput = e => {
        const { value } = e.target
        setValue(value)
    }
    
    const Options = () => {
        const addToQueue = e => {
            const songUri = e.target.dataset.songUri
            voteSong( songUri, roomCode,  +1);
            closeSearchUI()
        }
        return searchResults.items.map((i) => {
            return html`
                <button onClick=${addToQueue} data-song-uri=${i.uri} class="w-full bg-gray-200 border mb-2 rounded-lg hover:bg-gray-300">   
                    <div class="pointer-events-none">
                        ${i.name} — ${i.artists[0].name} <span class="opacity-50">${i.uri}</span>
                    </div>
                
                </button>
            `
        })
    }
    
    return (
        html`
        <button onClick=${openSearchUI}>open search</button>
        <div class="h-full w-full fixed top-0 bottom-0 left-0 right-0 bg-black bg-opacity-50 z-50 p-8 overflow-scroll">
            <div class="base mx-auto m-8">
              <div class="bg-white text-black p-8 py-10  w-full rounded-lg shadow-lg overflow-scroll relative">
                  <div class="top-0 right-0 absolute">
                      <button onClick=${closeSearchUI} class="p-1 mt-2 m-1 text-gray-600 hover:text-gray-800 leading-none"><i class='bx bxs-x-circle'></i></button>
                      
                  </div>
                  <form onSubmit=${onSubmit} action="#" class="mb-4">
                      <input type="search" name="search" class="form-input block w-full mt-1 rounded text-black text-xl" value=${value} onInput=${onInput} placeholder="Search for a song" autoFocus/>
                      <button type="submit" class="mt-2 bg-page-bg w-full py-2 text-page-contrast rounded">Search</button>
                  </form>
                  <div>
                      Results: please ignore bad ui
                      
                      ${searchResults ? Options() : "empty"}
                  </div>
              </div>
    
            </div>
        </div>
        
        `
    )
    }