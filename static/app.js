document.addEventListener("DOMContentLoaded", () => {
    const citySelect = document.getElementById("city-select");
    const mallList = document.getElementById("mall-list");
    const mallDetails = document.getElementById("mall-details");

    // Şehir listesini backend'den al
    fetch("/cities")
        .then((response) => response.json())
        .then((cities) => {
            cities.forEach((city) => {
                const option = document.createElement("option");
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
        });

    // Şehir seçildiğinde AVM listesini al
    citySelect.addEventListener("change", () => {
        const selectedCity = citySelect.value;
        fetch(`/malls?city=${selectedCity}`)
            .then((response) => response.json())
            .then((malls) => {
                mallList.innerHTML = "<h2>AVM Listesi</h2>";
                const ul = document.createElement("ul");
                malls.forEach((mall) => {
                    const li = document.createElement("li");
                    li.textContent = `${mall.Name}`;
                    li.addEventListener("click", () => showMallOptions(mall.MallID, mall.Name));
                    ul.appendChild(li);
                });
                mallList.appendChild(ul);
                mallDetails.innerHTML = ""; // Yeni şehir seçildiğinde detayları temizle
            });
    });



    

    


    // AVM seçeneklerini göster (Butonlar)
    function showMallOptions(mallId, mallName) {
        mallDetails.innerHTML = `
            <h2>${mallName} Detayları</h2>
           
            <div class="button-container">
                <button class="btn btn-primary" onclick="window.location.href='/mall_details/events/${mallId}'">Etkinlikler</button>
                <button class="btn btn-secondary" onclick="window.location.href='/mall_details/stores/${mallId}'">Mağazalar</button>
                <button class="btn btn-tertiary" onclick="window.location.href='/mall_details/parkings/${mallId}'">Otopark Bilgileri</button>
                <button class="btn btn-lost" onclick="window.location.href='/mall_details/lost_items/${mallId}'">Kayıp Eşyalar</button>
            </div>
        `;
    }
});
function filterStores() {
    const searchInput = document.getElementById("store-search").value.toLowerCase();
    const storeItems = document.querySelectorAll(".store-item");

    storeItems.forEach((item) => {
        const storeName = item.querySelector("strong").textContent.toLowerCase();
        if (storeName.includes(searchInput)) {
            item.style.display = "block"; // Eşleşiyorsa göster
        } else {
            item.style.display = "none"; // Eşleşmiyorsa gizle
        }
    });
}