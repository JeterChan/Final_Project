function getRating(){
    var  stars = document.querySelectorAll(".stars i");
    console.log(stars);
    var ratingResult = document.getElementById("stars-score");
    printRatingResult(ratingResult);
    stars.forEach((star,index1)=> {
        star.addEventListener("click",() => {        
            stars.forEach((star,index2) => {
                index1 >= index2 ? star.classList.add("active") : star.classList.remove("active");
                console.log(index2);
            });
            printRatingResult(ratingResult,index1+1);
            // 取最後一個 index1 為評分的值 需要+1 因為index從0開始計算
        });
    });
}

function printRatingResult(result,num=0){
    result.textContent = `${num}/5`;
}

function listenforLike(){
    var likes = document.querySelectorAll(".like");
    likes.forEach(like => {
        like.addEventListener("click",(event) => {
            event.target.classList.toggle("like-no");
            event.target.classList.toggle("like-yes");
            if(event.target.classList.contains("like-yes")) {
                console.log("Saving Favorite...");
            }
            else {
                console.log("Remove Favorite...");
            }
        })

    })
}

getRating();
listenforLike();
