import {xu} from "xu";
import {Format} from "../../Format.js";

export class ymst extends Format
{
	name         = "YMST Module";
	ext          = [".ymst", ".ym"];
	magic        = ["YM2149 song"];
	metaProvider = ["musicInfo"];
	notes        = xu.trim`
		UADE123 is the ONLY player I could find on linux and it only works with some YMST files I encountered. (ym.atomix doesn't work for example, see item #273 for more)
		Most other players (zxtune and audio overload) just wrap uade and have the same problems with the same files.
		XMPlay on Windows with the Delix plugin ((both in sandbox/app) https://support.xmplay.com/files_view.php?file_id=499) plays YMST files and outputs to WAV.
		Sadly it also fails to play the same YMST files that UADE123 chokes on. So, meh, guess I'm just outta luck here.`;
	converters   = ["uade123[player:YM-2149][maxDuration:300]"];	// most YM songs are just loops that go for like 8 minutes, let's limit it to 5
}
