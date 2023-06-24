const  stars = document.querySelectorAll(".stars i");
const ratingResult = document.getElementById("stars-score")

printRatingResult(ratingResult)

function getRating(stars){
    stars.forEach((star,index1)=> {
        star.addEventListener("click",() => {        
            stars.forEach((star,index2) => {
                index1 >= index2 ? star.classList.add("active") : star.classList.remove("active")
            })
            printRatingResult(ratingResult,index1+1)
            console.log(index1)// 取最後一個 index1 為評分的值 需要+1 因為index從0開始計算
        });
    });
}

function printRatingResult(result,num=0){
    result.textContent = `${num}/5`;
}


getRating(stars);
