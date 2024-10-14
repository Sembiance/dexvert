import {Format} from "../../Format.js";

export class zoomBrowserExThumbnailCache extends Format
{
	name           = "ZoomBrowser Ex thumbnail cache";
	website        = "http://fileformats.archiveteam.org/wiki/ZoomBrowser_Ex_thumbnail_cache";
	ext            = [".info"];
	forbidExtMatch = true;
	magic          = ["ZoomBrowser Ex thumbnails", /^fmt\/1496( |$)/];
	converters     = ["foremost"];
}
