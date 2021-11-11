
const r = await fetch("https://webhook.site/d2697520-afec-42d9-a772-3b338a9011d1", {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({imagePath : "/path/to/image.png"})});
console.log(r);
