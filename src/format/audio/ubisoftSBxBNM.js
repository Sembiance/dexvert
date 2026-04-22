import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ubisoftSBxBNM extends Format
{
	name         = "Ubisoft SBx BNM Audio";
	ext          = [".bnm"];
	idCheck      = async inputFile => inputFile.size>4 && (await fileUtil.readFileBytes(inputFile.absolute, 4)).indexOfX([0x00, 0x00, 0x00, 0x00])===0;
	metaProvider = ["ffprobe[libre]"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.nbStreams || 0)).map(i => `ffmpeg[libre][format:ubibnm][outType:mp3][numStreams:${dexState.meta.nbStreams}][streamNum:${i}]`).join(" & ")]);
}
