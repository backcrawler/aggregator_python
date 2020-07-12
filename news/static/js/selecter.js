function selectEverything(flag) {
    let block = document.getElementById('userpost-form');
    let sitesResults = block.querySelectorAll('[name^=sites]');
    let catResults = block.querySelectorAll('[name^=categories]');
    sitesResults.forEach(function(item) {
      item.checked = flag;
    })
    catResults.forEach(function(item) {
      item.checked = flag;
    })
}
