
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
    let wa_link = `https://api.whatsapp.com/send/?phone=${match[0].trim()}&text=hola%20amor,%20tj%20from%20tinder&app_absent=0`
    console.log(wa_link)
    document.querySelector('div').innerHTML = `<h1><a href="${wa_link}" target="_blank">wa.me</a></h1>`
    console.log(phone_numbers)
    return;
  }
  console.log(phone_numbers);
  return
}
});