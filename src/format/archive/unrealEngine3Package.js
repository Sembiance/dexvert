import {Format} from "../../Format.js";

export class unrealEngine3Package extends Format
{
	name           = "Unreal Engine 3 Package";
	ext            = [".u", ".uasset", ".utx", ".uax", ".umx", ".unr", ".ut3", ".upk"];
	forbidExtMatch = true;
	magic          = ["UE3 Unreal Package (LE)", "Format: UnrealEngine\\Unreal Package", /^Unreal (Audio|Engine) package/, /^Rune map$/, /^geArchive: U_\d+( |$)/, /^geArchive: UE3_\d+( |$)/];
	forbiddenMagic = ["Unreal Music"];
	idMeta         = ({macFileType, macFileCreator}) => ["UnDt", "UnMp", "UnMu", "UnSn", "UnTx"].includes(macFileType) && ["DsEx", "Rune", "Unrl", "UnTn"].includes(macFileCreator);
	converters     = ["gameextractorCLI"];
}
