
window.addEventListener("load", function(){
    //everything is fully loaded, don't use me if you can use DOMContentLoaded
    var form = document.querySelector("form");
form.onsubmit = (e) => {
  e.preventDefault();
  var input = e.target.querySelector("input");
  const string = input.value;
  console.log(input.value)
  let phone_numbers = [];
  const regexp = new RegExp("\\+?\\(?\\d*\\)? ?\\(?\\d+\\)?\\d*([\\s./-]?\\d{2,})+","g");
  phone_numbers = [...string.matchAll(regexp)];
  for (const match of phone_numbers) {
    let wa_link = `https://wa.me/${match[0].trim()}`
    console.log(wa_link)
    window.location.replace("http://stackoverflow.com");
    window.location.href = 'https://www.google.com'
    document.write('<br />');
  }
  console.log(phone_numbers);
  return
}
});