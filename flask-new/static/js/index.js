function getRating(){
    var  stars = document.querySelectorAll(".{{news_id}} p");
    console.log(stars);
    var ratingResult = document.querySelector(".{{news_id}} span");
    printRatingResult(ratingResult);
    stars.forEach((star,index1)=> {
        star.onclick = function() {
            let current_star_level = index1+1;
            console.log(index1+1)
            stars.forEach((star,index2) => {
                console.log(index2)
                if(current_star_level >= index2+1 )
                {
                    star.innerHTML = '&#9733';
                } else{
                    star.innerHTML = '&#9734';
                }
            });
            printRatingResult(ratingResult,index1+1);
            // 取最後一個 index1 為評分的值 需要+1 因為index從0開始計算
        };
    })
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


