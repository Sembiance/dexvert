import {Format} from "../../Format.js";

export class unityAssetsFile extends Format
{
	name           = "Unity Assets File";
	ext            = [".assets"];
	forbiddenExt   = [".unity3d"];	// archive/unityAssetBundle
	forbidExtMatch = true;
	magic          = [/^geArchive: ASSETS_\d+( |$)/, "Archive: Unity/Unity Asset", "archive:Unity.UnityAssetOpener"];
	weakMagic      = true;
	converters     = ["gameextractor[codes:NONE]", "GARbro[types:archive:Unity.UnityAssetOpener]"];
}
