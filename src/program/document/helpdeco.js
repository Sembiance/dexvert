/*
import {Program} from "../../Program.js";

export class helpdeco extends Program
{
	website = "https://sourceforge.net/projects/helpdeco/";
	gentooPackage = "app-arch/helpdeco";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://sourceforge.net/projects/helpdeco/",
	gentooPackage : "app-arch/helpdeco",
	gentooOverlay : "dexvert"
};

exports.bin = () => "helpdeco";

exports.pre = (state, p, r, cb) =>
{
	r.helpdecoTmpDirPath = fileUtil.generateTempFilePath();
	fs.mkdir(r.helpdecoTmpDirPath, {recursive : true}, cb);
};

exports.args = (state, p, r, inPath=state.input.absolute) => (["-r", "-y", inPath]);
exports.runOptions = (state, p, r) => ({cwd : r.helpdecoTmpDirPath, timeout : XU.MINUTE*4});

const fldinstRegex = /{\\field\s+{\\\*\\fldinst\s+import\s+(?<fileName>[^}]+)}}/;
const brokenImageHexData = "89504e470d0a1a0a0000000d4948445200000080000000800806000000c33e61cb00000006624b474400ff00ff00ffa0bda793000007e649444154789ced9d598c144518c77f3b3b1ec82e84851561e530410d284a44c1234262f08e4134f8200f5e892f02be299118828a068d313e29a031117d219c895114352a2831ec0262808807b80872392a2cee728e0fdf4c326c6666b7aabbaa7bbabf5f520f3b3bd5f5afeeff5477d7f11554a70e9800bc0c6c0076039d40de302deaa19c722cb22827aec957fd3b916bb41e5800dc805c432ba6005b2c44a801e255ffedc0f44a8564ca7cd608ac06d601e32c842bf1620cb00c58093474ff6777030c07be03a6bad7a578661a726d87957e586a8006e023e06a8fa214bf8c05d602fd8a1f941ae083c2179464330678aff847d100f7a0cd7e9a7800b813c40075c02b91ca51a26021509741def3af89588ce29f6b81f119b4e94f335333c0a4a85528913139035c1ab50a25325ab2c0e0100e741ad80be42afcbfdde298ed409bb5a2781176fd9b900e9dacb522612804eb673e00cc2c0852fcd204cc020e12ec1a5a676c0386b8aea5d2234381cd7836c001f4e2c789a1c0213c1a60a6976a2926ccc693014ea1f7fc3832107918776e805f3d554831673786d7b3dc84909ef82714a98a0b2abd8657c4c600798b3c8a1f8caf8d8d019404a10648396a8094a30648395960b1611e9b810dc50fab48ce009aa2288aa2288aa22889a10198036c023ab01bc3ce015f028f02f55ed59f4b3df058414b0ebbba7420e7e259a0af5ff9fe1907fc8edd89aa94be259c89ada65c026cb4d05b2ded41166c249211d84f5bea29b50217faab0a7d08360faf5a3a882cd34f1c2b7073c28a698ebfaaf09cc37ae491800e8962307006b7276d0f01e2e11850877487bbaccb19e416e31c5f8341377a286b0485850e8e69a15b940d071417ed3a278b7900a37624029509cd86dfb7e562609fe3327cd5c5a69cb9183e3f6481270d0b69c3dc00be5a1a1fe5f8aa8bcdebed3460bc49069d0f9072d40029470d9072d40029470d9072d40029470d9072d40029470d9072d40029470d90727c19a0cb53399d1eca48525dbc19608f87328ab10a5db31719af77cd6e0f657833c046e02fc7657c0d1c735c06c051e01bc7651c01be775c06e0cf00a7701b923e0fbce0f0f8dd79b150a62b1620e7cc0ba6d3955a2dcbc920ab575d4ca17ade525310e605d05b2dadc0fe87d96a519e3703804c405980ddde83e5d261646d40543c5ed010465d3a919625c83a076303d461de94b501d70710093249f43e64ff1a9bc51039644fc38f91851551d200dc8bac79b0899fd801ec4036ec3a18504b2b863382c06f0ba0b8c5b805d08ea094a30648396a8094a30648396a8094a30648396a8094a306483941b71dab15fa2191374623fb248e40165f9e07f4477e087f23c3bc87813f0ae927a4c7d1f548666424d500038029c01dc0646014c16207ec05d6039f019f229b662586a474055f808c2f2c034ee266a4aef41c3c8decd31327623f1ae882fe4884ad23b8bde8e55217125f212e317d526580bec04bd8879a0b339d04de060639ad71cfa4c6000f21f7e5a82f7cf79443b6738deaed2af1066804deafa02b4ee90bfcc42bea4ea20d3006f8b9971ae3900e216f203e49ec7c809b9059bfa3a216624033f2daf870d442aa510bfd007702ab093f126827f027f02f7016e93b68466e3361713eb01479605d12e2714325ceb78009c85cff309ae49dc042a4afa0dafd7910d281341f99ff783684b24f2311bc5c93a8678091049f717b0278078b8992255c09bc41f0d7cd4e6062001dbd213106c82251c0839cf065c065216a1a0cbc45b090b7bf211d57ae488c01e65be82aa61c6e9bdb5b09d607f1a1436d8930c028a4e9b639b9bb80cb1deb03690d82ec15709b235d8930806d58f99dc010c7da4a690436586add829bdec29a37c0440b3d79e46131ccfb7d6f69c2be73ca45ff40cd1b60a9859eb3485f41548cc5ee96b5d181969a36403332bc6aaae75d477a4c98875d2b705dc83a6ada00b32cb4fc87a79d357aa00fb01f73fd6f86aca3a6c702eeb6c8b384784ccfea045eb5c86753e7d089430bd007386ea165ac032db63461770b0b7380cbb805c8028b0d0b690f4b6d0913808b0cf36c057e74a0c5961cf00970bf61bec9c02f216958858c5fd41c4f61fecb792d12a5d5b1a9c7eb91282d10976780d11679d687ae223836d1c3ae0a5d85017131c01516797686ae2238bb308f216853f7d0888b014c63eb9cc6532045434e601eac72800b21bd252e06e867f8fd638809e248cef0fb8df8d9f1b42c713180e934ace34e54848369d4b27accdf801445511445511445512ca943d6b79bd08ef9f6f18a1fe66211ab200ec3c14a38d4f484102502d40029470d9072d40029c7c600918d5c293d627c6d6c0c10e9f8b55215abb885a6af81a7b0db1c4971cb20648e84f3d7c02c302304c14ab8ccc072cb39d316208f6c6f16451834a53c2dd84753b1ca940736a32688032dc87273dbeb689d318fc4c29b4dfc8226a7818148c0ea407194ea90756d4143b09d4166c3568aabbf0af301a4b9f889ace583b0eb3f101846b06d6601bab2c8e2ca91010f545f3846a5e3d82c571a4eb0e85e7122aef5df9701f6392e44892ffb33480856259d7c9501d644ad42898c35196013f043d44a14ef6c05366790d78139118b51fcf30c255dc16b8195118a51fcb21c5807e78e063e026c8b448ee2931dc013c53f4a0dd08184528f53d815255cb6017701478b1f741f0d6c076e466f07496439700bdde217941b0eee001e046e47061994da663bd2b24fa7ccd2f56a5bc67c8e74458e47225f4d42f6dd1d42f8dbb728e1d08504acdc8774f0ad41baa1f39532fc0f6274fa6b39c01d0d0000000049454e44ae426082";	// eslint-disable-line max-len

// WARNING: The below is somewhat fragile, especially with the image converting that is taking place
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function locateRTF()
		{
			fileUtil.glob(r.helpdecoTmpDirPath, "*.rtf", {nodir : true}, this);
		},
		function loadRTF(rtfFilePaths=[])
		{
			if(rtfFilePaths.length!==1)
				return this.jump(-1);

			this.data.rtfFilePath = rtfFilePaths[0];

			fs.readFile(rtfFilePaths[0], XU.UTF8, this);
		},
		function convertImagesToPDF(rtfRaw)
		{
			this.data.rtfLines = rtfRaw.toString("utf8").split("\n");
			this.data.bitmapFilePaths = [];

			this.data.rtfLines.forEach(line =>
			{
				const parts = line.match(fldinstRegex);
				if(!parts)
					return;
				
				this.data.bitmapFilePaths.push(path.join(r.helpdecoTmpDirPath, parts.groups.fileName));
			});

			if(this.data.bitmapFilePaths.length===0)
				return this.jump(-2);
			
			// Convert SHG files
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) =>
			{
				if(bitmapFilePath.endsWith(".shg"))
					p.util.program.run("deark", {argsd : [bitmapFilePath, r.helpdecoTmpDirPath, path.basename(bitmapFilePath)]})(state, p, subcb);
				else
					setImmediate(subcb);
			}, this);
		},
		function convertToPNG()
		{
			XU.log`convertToPNG`;
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) =>
			{
				if(bitmapFilePath.endsWith(".shg"))
					p.util.program.run("convert", {argsd : [`${bitmapFilePath}.000.bmp`, `${bitmapFilePath}.png`]})(state, p, subcb);
				else
					p.util.program.run("convert", {argsd : [bitmapFilePath, `${bitmapFilePath}.png`]})(state, p, subcb);
			}, this);
		},
		function loadImages()
		{
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) => fs.readFile(`${bitmapFilePath}.png`, (err, fileData) =>
			{
				if(err && state.verbose>=1)
					XU.log`helpdeco was unable to access PNG ${bitmapFilePath} with err ${err}`;

				subcb(undefined, err ? null : fileData);
			}), this);
		},
		function embedImagesIntoRTF(imagesFileData)
		{
			let i=0;
			fs.writeFile(this.data.rtfFilePath, this.data.rtfLines.map(line =>
			{
				if(!fldinstRegex.test(line))
					return line;
				
				const imageData = imagesFileData[i] ? imagesFileData[i].toString("hex").toLowerCase() : brokenImageHexData;
				i++;

				return line.replace(fldinstRegex, `{\\pict\\pngblip\n${imageData}}`);
			}).join("\n"), XU.UTF8, this);
		},
		function convertRTFToPDF()
		{
			p.util.program.run("soffice", {flags : {sofficeType : "pdf"}, argsd : [this.data.rtfFilePath]})(state, p, this);
		},
		function cleanup()
		{
			fileUtil.unlink(r.helpdecoTmpDirPath, this);
		},
		cb
	);
};
*/
