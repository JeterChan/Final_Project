const  stars = document.querySelectorAll(".stars i");
const ratingResult = document.getElementById("avg-stars");


printRatingResult(ratingResult);

function getRating(stars,result){
    stars.forEach((star,index1)=> {
        star.addEventListener("click",() => {        
            stars.forEach((star,index2) => {
                index1 >= index2 ? star.classList.add("active") : star.classList.remove("active")
            })
            printRatingResult(result,index1+1);
            console.log(index1)// 取最後一個 index1 為評分的值 需要+1 因為index從0開始計算
        });
    });
}

function printRatingResult(result,num=0){
    result.textContent = `${num}/5`;
}


getRating(stars,ratingResult);


// const ratingStars = [document.getElementsByClassName("rating")];


// function executeRating(stars) {
//    const starClassActive = "fa-solid fa-star star";
//    const starClassUnactive = "fa-regular fa-star star";
//    const starsLength = stars.length;
//    let i;
//    stars.map((star) => {
//       star.onclick = () => {
//          i = stars.indexOf(star);

//          if (star.className.indexOf(starClassUnactive) !== -1) {

//             for (i; i >= 0; --i) stars[i].className = starClassActive;
//          } else {

//             for (i; i < starsLength; ++i) stars[i].className = starClassUnactive;
//          }
//       };
//    });
// }


// executeRating(ratingStars);