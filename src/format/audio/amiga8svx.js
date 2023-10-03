import {xu} from "xu";
import {Format} from "../../Format.js";

export class amiga8svx extends Format
{
	name         = "Amiga 8-bit Sampled Voice";
	website      = "http://fileformats.archiveteam.org/wiki/8SVX";
	ext          = [".8svx", ".iff"];
	weakExt      = [".iff"];
	magic        = ["Amiga IFF 8SVX audio", "IFF data, 8SVX", "Interchange File Format 8-bit Sampled Voice", /^fmt\/339( |$)/];
	notes        = xu.trim`
		Some 8SVX files don't have a sample rate in the file (test3.iff, sample01.ek___D.8svx). In these cases I try multiple different common sample rates.
		SDL library I could use to create an 8svx2wav program: https://github.com/svanderburg/SDL_8SVX`;
	metaProvider = ["soxi"];
	converters   = async dexState =>
	{
		const inputData = await Deno.readFile(dexState.f.input.absolute);
		const vhdrLoc = inputData.indexOfX("VHDR");
		let voiceRate = null;
		if(vhdrLoc!==-1)
		{
			const offsetLoc = vhdrLoc+20;
			const fileRate = inputData.getUInt16BE(offsetLoc);
			if(fileRate===1)
			{
				// 1Hz is likely meant to be 8khz
				voiceRate = 8000;	// 8000, 11025, 16000, 22050, 32000, 37800, 44100, 48000
			}
			else if(fileRate===0)
			{
				// 0Hz is a bug and ffmpeg won't even convert them. So we fill in a sample rate and cross our fingers
				inputData.setUInt16BE(offsetLoc, 8000);
				await Deno.writeFile(dexState.f.input.absolute, inputData);	// safe to do since we copied it over to RAM
			}
		}

		return [`ffmpeg[outType:mp3]${voiceRate ? `[rate:${voiceRate}]` : ""}`, "iff_convert -> sox"];	// The last entry used to be: , "amiga8SVXtoXXX[matchType:magic]"
	};
}
