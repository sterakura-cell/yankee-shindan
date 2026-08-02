/**
 * build-assets.js — img/<CODE>.png から公開アセットを再生成する（ヤンキー診断）
 * 生成: og.png(1200x630グリッド) / card/<CODE>.png / t/<CODE>.html
 * 使い方: cd tools && npm install && node build-assets.js
 */
const fs=require("fs"), path=require("path");
const { PNG }=require("pngjs");
const ROOT=path.join(__dirname,"..");
const CONFIG={
  siteName:"ヤンキータイプ診断",
  domain:"https://yankee.soter-info.com",
  hashtag:"#ヤンキータイプ診断",
  bg:{r:0x17,g:0x14,b:0x1b},
  gold:{r:0xe3,g:0xb2,b:0x3c},
  red:{r:0xd6,g:0x45,b:0x45},
  faviconCode:"KOAS",
  order:["KBAT","KBAS","KBCT","KBCS","KOAT","KOAS","KOCT","KOCS","NBAT","NBAS","NBCT","NBCS","NOAT","NOAS","NOCT","NOCS"],
  names:{
    KBAT:"情緒不安定な特攻隊長",KBAS:"強奪系レディース女帝",KBCT:"潔癖すぎるレディース総長",KBCS:"語彙力ゼロのクール参謀",
    KOAT:"すぐ謝る武闘派",KOAS:"カツアゲ未遂リーゼント",KOCT:"女々しいスキンヘッド",KOCS:"陰キャレディース一匹狼",
    NBAT:"情に厚すぎて泣く兄貴",NBAS:"見た目だけレディース番長（中身小学生）",NBCT:"ビビりのカリスマレディース総長",NBCS:"実家が太い偽ワル",
    NOAT:"方向音痴の走り屋",NOAS:"ママ大好き夜露死苦マン",NOCT:"甘党すぎるスケバン",NOCS:"めそめそレディース番長",
  },
};
function readPNG(p){return PNG.sync.read(fs.readFileSync(p));}
function solid(w,h,c){const png=new PNG({width:w,height:h});for(let i=0;i<w*h;i++){png.data[i*4]=c.r;png.data[i*4+1]=c.g;png.data[i*4+2]=c.b;png.data[i*4+3]=255;}return png;}
function paste(dst,W,tile,dx,dy,size){
  const scale=tile.width/size;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const sx=x*scale,sy=y*scale,x0=Math.floor(sx),y0=Math.floor(sy),x1=Math.min(x0+1,tile.width-1),y1=Math.min(y0+1,tile.height-1),fx=sx-x0,fy=sy-y0,px=[];
    for(let c=0;c<4;c++){const v00=tile.data[(y0*tile.width+x0)*4+c],v10=tile.data[(y0*tile.width+x1)*4+c],v01=tile.data[(y1*tile.width+x0)*4+c],v11=tile.data[(y1*tile.width+x1)*4+c];px[c]=v00*(1-fx)*(1-fy)+v10*fx*(1-fy)+v01*(1-fx)*fy+v11*fx*fy;}
    const a=px[3]/255;if(a<=0.01)continue;const di=((dy+y)*W+(dx+x))*4;
    for(let c=0;c<3;c++)dst.data[di+c]=Math.round(px[c]*a+dst.data[di+c]*(1-a));
  }
}
function bars(dst,W,H){
  for(let y=0;y<12;y++)for(let x=0;x<W;x++){const t=(y*W+x)*4,b=((H-1-y)*W+x)*4;dst.data[t]=CONFIG.gold.r;dst.data[t+1]=CONFIG.gold.g;dst.data[t+2]=CONFIG.gold.b;dst.data[b]=CONFIG.gold.r;dst.data[b+1]=CONFIG.gold.g;dst.data[b+2]=CONFIG.gold.b;}
  for(let y=14;y<18;y++)for(let x=0;x<W;x++){const t=(y*W+x)*4,b=((H-1-y)*W+x)*4;dst.data[t]=CONFIG.red.r;dst.data[t+1]=CONFIG.red.g;dst.data[t+2]=CONFIG.red.b;dst.data[b]=CONFIG.red.r;dst.data[b+1]=CONFIG.red.g;dst.data[b+2]=CONFIG.red.b;}
}
(function main(){
  const W=1200,H=630,imgDir=path.join(ROOT,"img");
  for(const code of CONFIG.order){if(!fs.existsSync(path.join(imgDir,code+".png")))throw new Error("img/"+code+".png が無い");}
  fs.mkdirSync(path.join(ROOT,"card"),{recursive:true});
  fs.mkdirSync(path.join(ROOT,"t"),{recursive:true});
  const og=solid(W,H,CONFIG.bg);
  const SIZE=138,GAP=8,rowW=8*SIZE+7*GAP,x0=Math.round((W-rowW)/2),rowsY=[95,340];
  CONFIG.order.forEach((code,i)=>{const tile=readPNG(path.join(imgDir,code+".png"));paste(og,W,tile,x0+(i%8)*(SIZE+GAP),rowsY[Math.floor(i/8)],SIZE);});
  bars(og,W,H);
  fs.writeFileSync(path.join(ROOT,"og.png"),PNG.sync.write(og));
  for(const code of CONFIG.order){
    const card=solid(W,H,CONFIG.bg),tile=readPNG(path.join(imgDir,code+".png"));
    paste(card,W,tile,Math.round((W-540)/2),40,540);bars(card,W,H);
    fs.writeFileSync(path.join(ROOT,"card",code+".png"),PNG.sync.write(card));
    const name=CONFIG.names[code],title="あなたの中のヤンキーは『"+name+"』でした！";
    const desc="12問で判定！強面×残念ギャップの16タイプ診断。あなたはどのヤンキー？ "+CONFIG.hashtag;
    const html='<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>'+title+'｜'+CONFIG.siteName+'</title>\n'+
      '<meta name="description" content="'+desc+'">\n<meta name="robots" content="noindex,follow">\n'+
      '<meta property="og:type" content="website">\n<meta property="og:site_name" content="'+CONFIG.siteName+'">\n<meta property="og:locale" content="ja_JP">\n'+
      '<meta property="og:title" content="'+title+'">\n<meta property="og:description" content="'+desc+'">\n'+
      '<meta property="og:url" content="'+CONFIG.domain+'/t/'+code+'.html">\n<meta property="og:image" content="'+CONFIG.domain+'/card/'+code+'.png">\n'+
      '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'+
      '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="'+title+'">\n<meta name="twitter:description" content="'+desc+'">\n<meta name="twitter:image" content="'+CONFIG.domain+'/card/'+code+'.png">\n'+
      '<link rel="canonical" href="'+CONFIG.domain+'/">\n<meta http-equiv="refresh" content="0; url=/?type='+code+'">\n<link rel="icon" type="image/png" href="/img/'+CONFIG.faviconCode+'.png">\n</head>\n'+
      '<body><p><a href="/?type='+code+'">'+CONFIG.siteName+'で結果を見る</a></p></body>\n</html>\n';
    fs.writeFileSync(path.join(ROOT,"t",code+".html"),html);
  }
  console.log("done: og.png + card/*.png(16) + t/*.html(16)");
})();
