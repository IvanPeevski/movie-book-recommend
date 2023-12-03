const messages = {
  'book': 'Book 📖',
  'movie': 'Movie 🎥',
  'bookPlaceholder': 'Enter a favorite book, e.g. "The Great Gatsby"',
  'moviePlaceholder': 'Enter a favorite movie, e.g. "Seven Samurai"',
};
const bookRadio = document.querySelector('#book');
const movieRadio = document.querySelector('#movie');
const dropDown = document.querySelector('#autocomplete-dropdown');
const listBox = dropDown.querySelector('.autocomplete-results');
const searchInput = document.querySelector('#search-input');
let activeView = 'book';
selectedItem = null;
window.onload = function() {
  initRadioButton();
  initSearch();
}

function initRadioButton(){
  
  bookRadio.addEventListener('change', checkState);
  movieRadio.addEventListener('change', checkState);

  checkState();
}

function initSearch(){
  let debounceTimer;
  function debounce(func, delay) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(func, delay);
  }
  searchInput.addEventListener('input', function(event) {
    var val = this.value;
    if (val.length < 2) {
        closeDropDown();
        return;
    }
    debounce(function() {
        getOptions(val);
    }, 300);

  });
  searchInput.addEventListener('focus', function(event) {
    dropDown.setAttribute('closed', listBox.childElementCount == 0);
  });
  searchInput.addEventListener('blur', function(event) {
    setTimeout(function() {
      dropDown.setAttribute('closed', true);
    }, 100);
  });

  const includedAdaptations = document.querySelector('#include-adaptations')
  includedAdaptations.addEventListener('change', function(event) {
    if(selectedItem){
      getRecommendations(selectedItem.id);
    }
  });
}

function closeDropDown() {
  dropDown.setAttribute('closed', true);
}

function openDropDown() {
  dropDown.setAttribute('closed', false);
  if(activeView === 'movie'){
    dropDown.querySelector('.attribution').innerHTML = 'Search results provided by Google Books';
  }
  else{
    dropDown.querySelector('.attribution').innerHTML = 'Search results provided by The Movie Database';
  }
}

function getOptions(query){
  const type = activeView === 'book' ? 'movie' : 'book';
  const includeAdult = document.querySelector('#include-adult').checked;
  const includedAdaptations = document.querySelector('#include-adaptations').checked;
  fetch(`/search?query=${encodeURIComponent(query)}&type=${type}&include_adult=${includeAdult}&include_adaptations=${includedAdaptations}`)
  .then(response => response.json())
  .then(data => {
      loadItems(data);
  })
  .catch(error => {
      console.error('Error:', error);
      return [];
  });
}

function loadItems(items) {
  listBox.innerHTML = '';
  items.forEach(function(item, i) {
    let itemElement = createItemElement(item);
    itemElement.setAttribute('tabindex', i + 1);
    listBox.appendChild(itemElement);
  });
  if(items.length == 0){
    closeDropDown();
  }
  else{
    openDropDown();
  }
}

function createItemElement(item) {
  let container = document.createElement("div");
  container.classList.add("autocomplete-item");
  let imageContainer = document.createElement("div");
  imageContainer.classList.add("autocomplete-item-image");
  let image = document.createElement("img");
  image.src = item.previewImage;
  imageContainer.appendChild(image);
  container.appendChild(imageContainer);

  let textContainer = document.createElement("div");
  textContainer.classList.add("autocomplete-item-text");
  textContainer.innerHTML = item.title;
  container.appendChild(textContainer);

  container.addEventListener("mousedown", function(event) {
    handleItemSelect(item);
  });

  return container;
}

function generateCard(item) {
  let card = document.createElement('div');
  card.className = 'result-card';

  let header = document.createElement('div');
  header.className = 'result-card-header';
  card.appendChild(header);

  let imageDiv = document.createElement('div');
  imageDiv.className = 'result-card-header-image';
  header.appendChild(imageDiv);

  if(item.previewImage){
    let image = document.createElement('img');
    image.src = item.previewImage;
    image.alt = 'Image cover';
    image.className = 'result-card-image';
    imageDiv.appendChild(image);
  }

  let textDiv = document.createElement('div');
  textDiv.className = 'result-card-header-text';
  card.appendChild(textDiv);

  let title = document.createElement('div');
  title.className = 'result-card-title';
  title.textContent = item.title;
  textDiv.appendChild(title);

  let description = document.createElement('div');
  description.className = 'result-card-description';
  if(item.authors){
    description.textContent = 'By ' + item.authors.join(', ') + ' | ' + item.year + ' | ' + item.rating + ' ⭐';
  }
 else{
    description.textContent = item.year + ' | ' + item.rating/2 + ' ⭐';
 }
  textDiv.appendChild(description);

  return card;
}

function checkState(){
  if (bookRadio.checked) {
    bookView();
  }
  else if (movieRadio.checked) {
    movieSelected();
  }

  listBox.innerHTML = '';
  closeDropDown();
}

function handleItemSelect(itemData) {
  searchInput.value = itemData.title;
  selectedItem = itemData;
  closeDropDown();
  getRecommendations(itemData.id);
}

function getRecommendations(itemId) {
  const includeAdult = document.querySelector('#include-adult').checked;
  const includedAdaptations = document.querySelector('#include-adaptations').checked;
  const params = `?id=${encodeURIComponent(itemId)}&include_adult=${includeAdult}&include_adaptations=${includedAdaptations}`;
  let fetchUrl = activeView === 'book' ? '/recommend_books' : '/recommend_movies';
  fetch(fetchUrl + params)
  .then(response => response.json())
  .then(data => {
      loadRecommendations(data);
  })
  .catch(error => {
      console.error('Error:', error);
      return [];
  });

  displayLoading();
}

function loadRecommendations(items) {
  let results = document.querySelector('.result-cards');
  results.innerHTML = '';
  items.forEach(function(item) {
    let card = generateCard(item);
    results.appendChild(card);
  });
}

function displayLoading() {
  let results = document.querySelector('#result-cards');
  results.innerHTML = '';
  results.setAttribute('loading', true);
  //display 4 empty cards
  cards = [];
  for (let i = 0; i < 4; i++) {
    let dummyObject;
    if(activeView === 'book'){
      dummyObject = {
        title: 'Book Title',
        authors: ['Author'],
        year: 'Year',
        rating: 'Rating',
        previewImage: '/static/images/loading.gif'
      }
    }
    else{
      dummyObject = {
        title: 'Movie Title',
        authors: ['Director'],
        year: 'Year',
        rating: 'Rating',
        previewImage: '/static/images/loading.gif'
      }
    }
    let card = generateCard(dummyObject);
    card.classList.add('loading');
    results.appendChild(card);
  }
}

function bookView() {
  document.querySelector('#input-addon').innerHTML = messages['movie'];
  document.querySelector('#search-input').placeholder = messages['moviePlaceholder'];
  document.querySelector('#search-input').value = '';
  activeView = 'book';
}

function movieSelected() {
  document.querySelector('#input-addon').innerHTML = messages['book'];
  document.querySelector('#search-input').placeholder = messages['bookPlaceholder'];
  document.querySelector('#search-input').value = '';
  activeView = 'movie';
}