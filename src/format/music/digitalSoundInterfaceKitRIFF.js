import {Format} from "../../Format.js";

export class digitalSoundInterfaceKitRIFF extends Format
{
	name         = "Digital Sound Interface Kit RIFF Module";
	ext          = [".dsm"];
	magic        = ["Digital Sound Interface Kit (RIFF) module", "RIFF Datei: unbekannter Typ 'DSMF'"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123", "gamemus[format:dsm-dsik]"];
}
