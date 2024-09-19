
import {Format} from "../../Format.js";

export class lowBitrateAudio extends Format
{
	name       = "Low- Bitrate Packed Audio";
	website    = "https://www.rarewares.org/rrw/lbpack.php";
	ext        = [".lb"];
	magic      = ["Low Bitrate Packer compressed audio", "Generic RIFF file LBit"];
	converters = ["lbplay"];
}
