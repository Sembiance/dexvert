import {Format} from "../../Format.js";

export class ueTexture2D extends Format
{
	name           = "Unreal Engine Texture";
	ext            = [".texture2d"];
	forbidExtMatch = true;
	magic          = [/^geViewer: UE3_Texture2D(_\d)?( |$)/];
	converters     = ["gameextractor[codes:UE3_Texture2D,UE4_Texture2D_7,UE4_Texture2D_6,UE4_Texture2D_5,UE4_Texture2D_4][renameOut]"];
}
