function getRating(){
    var  rate = document.querySelectorAll(".rating");
    console.log(rate);
    for(var i=0; i<rate.length; i++){
        let stars = document.getElementsByName(rate[i].dataset.id)
        console.log(stars)
        let ratingResult = document.getElementById(rate[i].dataset.id)
        console.log(ratingResult)
        printRatingResult(ratingResult);

        stars.forEach((star,index1)=> {
            console.log(star)
            // star.addEventListener("click",() => {
            //     stars.forEach((star,index2) => {
            //     index1 >= index2 ? star.classList.add("active") : star.classList.remove("active");
            //     console.log(index1);
            // });
            star.onclick = function() {
                console.log(star)
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
            };
               
            // 取最後一個 index1 為評分的值 需要+1 因為index從0開始計算
            
        });
    }

}


function printRatingResult(result,num=0){
    result.textContent = `${num}/5`;
}

function listenforLike(){
    var likes = document.querySelectorAll(".like");
    console.log(likes)

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
                    console.log(like.dataset.id)
                    // 可回傳like.datset.id => 會是收藏的主題名稱 型態為字串
                })
                
            })// end of forEach
    
       
} // end of listenforLike

function openMenu(evt, menuName, cardname) {
    var i, x, tablinks;
    x = document.getElementsByClassName("menu");
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < x.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" w3-dark-grey", "");
    }
    document.getElementById(menuName).style.display = "block";
    document.getElementById(cardname).style.display = "flex";
    evt.currentTarget.firstElementChild.className += " w3-dark-grey";
  }
  

listenforLike();
getRating();
