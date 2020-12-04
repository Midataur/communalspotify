function QueueItem({ uri, imageSrc, artist, title, voteCount }) {
  const alreadyVoted = getPreviouslyVotedSongs().includes(uri)
  const queueVoteSong = () => {
      if (alreadyVoted) {
        voteSong(uri, roomCode, -1)
        removeSongFromLocalStorage(uri)
      } else {
        voteSong(uri, roomCode, +1)
      }
      
  }
  return html`
    <div class="flex bg-page-contrast rounded-lg text-black items-center mb-4 shadow">
      <!--(art) (title / artist) (votebutton / counter) -->
      <div class="w-24">
        <div class="relative aspect-ratio-square rounded-lg ">
          <img
            src="${imageSrc}"
            class="absolute w-full h-full object-cover bg-page-contrast rounded-l-lg"
          />
        </div>
      </div>
      <div class="pl-4 flex-grow">
        <div class="text-lg mb-1">${title}</div>
        <div class="text-base text-gray-700">${artist}</div>
      </div>
      <button
        onClick=${queueVoteSong}
        class="w-24 text-center border-gray-300 border-l h-24 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-r-lg cursor-pointer ${alreadyVoted ? "text-page-bg" : ""}"
      >
        <div>
          <i class="bx bxs-upvote text-4xl"></i>
          <div class="text-gray-700 pt-2">${voteCount}</div>
        </div>
      </button>
    </div>
  `;
}

function Queue({}) {
  const [queueData, setQueueData] = useState([]);
  
  const fetchQueue = () =>
    fetch(`/api/getCurrentQueue?roomcode=${roomCode}`)
      .then((r) => r.json())
      .then((data) => setQueueData(data.sort((a,b) => b.score- a.score)))
      .catch(() => {
        error: "fetching queue state failed";
      })
      .then(() => console.log("Queue", queueData))
  
  // so it dont run on every frame lol.
  // ie, only run on component mount and dismount.
  useEffect(()=>{
    fetchQueue()
    socket.on('queue_change', function( ) {
      console.log('queued song');
      fetchQueue()
      /*const prevVotesSet = new Set(getPreviouslyVotedSongs())
      console.log("fetchQueue/prevVotes",prevVotesSet)
      const queueDataSet = queueData.map(i => i.foo);
      console.log("fetchQueue/queue",queueDataSet)
      const diff = [...prevVotesSet].filter(x => !queueDataSet.includes(x) );
      console.log("fetchQueue/diff",diff)*/
  });
  }, [])
  
  
   
  
  if (!queueData) return html`loading... <button onClick=${fetchQueue}>reload</button>`
  console.log(queueData)
  if (queueData.length === 0) return html`
    <div class="border-2 rounded-lg border-dashed border-page-contrast p-4 text-center">
      <div class="text-lg mb-1">Looks like there are no songs in the queue.</div>
      <div class="text-base opacity-75">Try adding some by pressing "open search"</div>
    </div>
  `
  
  const QueueList = queueData.map(({score, image, uri, name, artist})=> html`
  <${QueueItem}
    uri=${uri}
    imageSrc=${image}
    artist=${artist}
    title=${name}
    voteCount=${score}
  />
  `)  
    
  return html` 
     ${QueueList}
  `;
}
