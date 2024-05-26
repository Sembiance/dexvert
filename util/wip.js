/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil, cmdUtil} from "xutil";
import {path, delay, base64Encode, csvParse} from "std";
import {Program} from "../src/Program.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {identify} from "../src/identify.js";
import {getDetections} from "../src/Detection.js";
import {programs, init as initPrograms} from "../src/program/programs.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {MediaWiki} from "MediaWiki";
import {xmlParse} from "denoLandX";

const xlog = new XLog("info");
//await initPrograms(xlog);
//await initFormats(xlog);

const inputFile = await DexFile.create("/mnt/compendium/DevLab/dexvert/test/sample/image/macPaint/elvis.mac");
const getMacBinaryMeta = async () =>
{
	// MacBinary 1 Specs: https://web.archive.org/web/19991103230427/http://www.lazerware.com:80/formats/macbinary/macbinary.html
	// MacBinary 2 Specs: https://files.stairways.com/other/macbinaryii-standard-info.txt

	// MacBinary header is 128 bytes
	if(inputFile.size<128)
		return;

	const header = await fileUtil.readFileBytes(inputFile.absolute, 128);
	if([0, 74, 82].some(v => header[v]!==0))
		return xlog.error`zero byte not found at offset 0, 74, or 82`;

	if(header[1]>63)	// Also used to fail if header[1]<1 but then I discovered a file that has a header[1] of 0 (test/sample/audio/fssdSound/LABSLAB.SOU)
		return xlog.error`header[1] is greater than 63`;

	const dataForkLength = header.getUInt32BE(83);
	const resourceForkForkLength = header.getUInt32BE(87);
	if(dataForkLength===0 && resourceForkForkLength===0)
		return xlog.error`both dataForkLength and resourceForkForkLength are 0`;

	if((dataForkLength+128)>inputFile.size)	// I used to add resourceForkForkLength+128 but I encountered a file where that's not true (test/sample/audio/fssdSound/IFALLEN.SOU)
		return xlog.error`dataForkLength+128 is greater than the file size`;

	// here we check to see if the type or creator has a null byte. I think in theory null bytes are allowed and I think I've even encountered it (though I forget where), but since this macBinary check is weak in general, we just restrict matches to those with non-null bytes in the type/creator
	const fileTypeData = header.subarray(65, 69);
	if(fileTypeData.indexOfX(0)!==-1)
		return xlog.error`fileTypeData contains a null byte`;

	const fileCreatorData = header.subarray(69, 73);
	if(fileCreatorData.indexOfX(0)!==-1)
		return xlog.error`fileCreatorData contains a null byte`;

	const creationDate = header.getUInt32BE(91);
	const modifiedDate = header.getUInt32BE(95);

	// I used to do the following check, but I've encountered files (image/macPaint/elvis.mac) where the creation date is after the modified date by a lot, so we'll skip this check
	// ensure our modified date is not more than 2 days after our creation date (we've seen a few in the wild that are off by small amount, like 90 seconds (archive/macBinary/ZEN.HLP))
	//if((creationDate-modifiedDate)>((xu.DAY*2)/1000))
	//	return xlog.error`creationDate is greater than modifiedDate ${{creationDate, modifiedDate, difference : creationDate-modifiedDate, differenceInMinutes : (creationDate-modifiedDate)/(xu.MINUTE/1000)}}`;

	const macTSToDate = v => (new Date((v * 1000) + (new Date("1904-01-01T00:00:00Z")).getTime()));
	if(([macTSToDate(creationDate).getFullYear(), macTSToDate(modifiedDate).getFullYear()].some(year => year<1960 || year>(new Date()).getFullYear())) &&
	 ([new Date(creationDate*1000), new Date(modifiedDate*1000)].some(d => d.getFullYear()<1960 || d.getFullYear()>(new Date()).getFullYear())))
		return xlog.error`creationDate or modifiedDate is out of range (max epoc ${macTSToDate(creationDate)} ${macTSToDate(modifiedDate)}) (unix epoch ${new Date(creationDate*1000)} ${new Date(modifiedDate*1000)})`;

	return { macFileType : await encodeUtil.decodeMacintosh({data : fileTypeData}), macFileCreator : await encodeUtil.decodeMacintosh({data : fileCreatorData})};
};

xlog.info`${await getMacBinaryMeta()}`;

