export const allowedCities = new Set([
"Delhi","Mumbai","Kolkata","Bangalore","Chennai","Hyderabad","Pune","Ahmedabad","Surat","Lucknow",
"Jaipur","Kanpur","Mirzapur","Nagpur","Ghaziabad","Supaul","Vadodara","Rajkot","Vishakhapatnam",
"Indore","Thane","Bhopal","Pimpri-Chinchwad","Patna","Bilaspur","Ludhiana","Agra","Madurai",
"Jamshedpur","Prayagraj","Nasik","Faridabad","Meerut","Jabalpur","Kalyan","Vasai-Virar",
"Najafgarh","Varanasi","Srinagar","Aurangabad","Dhanbad","Amritsar","Aligarh","Guwahati",
"Haora","Ranchi","Gwalior","Chandigarh","Haldwani","Vijayawada","Jodhpur","Raipur","Kota",
"Bhayandar","Loni","Ambattur","Salt Lake City","Bhatpara","Kukatpalli","Dasarahalli",
"Muzaffarpur","Oulgaret","New Delhi","Tiruvottiyur","Puducherry","Byatarayanpur","Pallavaram",
"Secunderabad","Shimla","Puri","Murtazabad","Shrirampur","Chandannagar","Sultanpur Mazra",
"Krishnanagar","Barakpur","Bhalswa Jahangirpur","Nangloi Jat","Balasore","Dalupura","Yelahanka",
"Titagarh","Dam Dam","Bansbaria","Madhavaram","Abbigeri","Baj Baj","Garhi","Mirpeta","Nerkunram",
"Kendrapara","Sijua","Manali","Kankuria","Chakapara","Pappakurichchi","Herohalli","Madipakkam",
"Sabalpur","Bauria","Salua","Chik Banavar","Jalahalli","Chinnasekkadu","Jethuli","Nagtala",
"Pakri","Hunasamaranhalli","Hesarghatta","Bommayapalaiyam","Gundur","Punadih","Hariladih",
"Alawalpur","Madnaikanhalli","Bagalur","Kadiganahalli","Khanpur Zabti","Mahuli","Zeyadah Kot",
"Arshakunti","Mirchi","Sonudih","Bayandhalli","Sondekoppa","Babura","Madavar","Kadabgeri",
"Nanmangalam","Taliganja","Tarchha","Belgharia","Kammanhalli","Ambapuram","Sonnappanhalli",
"Kedihati","Doddajeevanhalli","Simli Murarpur","Sonawan","Devanandapur","Tribeni","Huttanhalli",
"Nathupur","Bali","Vajarhalli","Alija Kotla","Saino","Shekhpura","Cachohalli","Andheri",
"Narayanpur Kola","Gyan Chak","Kasgatpur","Kitanelli","Harchandi","Santoshpur","Bendravadi",
"Kodagihalli","Harna Buzurg","Mailanhalli","Sultanpur","Adakimaranhalli"
]);

export function validateInput(city, conditions) {
  if (!allowedCities.has(city)) {
    throw new Error("Invalid city. Only predefined cities allowed.");
  }

  if (!conditions || conditions.trim().length < 3) {
    throw new Error("Conditions input is too short.");
  }
}