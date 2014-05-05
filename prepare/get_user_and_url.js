var list = $x("//a[@action-type='usercard']")
for(i=0;i<100;i++){
	if(i%2==1){
		console.log(list[i].text+","+list[i].getAttribute("href"));
	}
}