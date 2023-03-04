import {xu, fg} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path} from "std";
import {RELEASE} from "../../release/RELEASE.js";

export default async function buildRelease(xlog)
{
	const tarballFilePath = path.join(RELEASE.TARBALL_DIR, `dexvert-${RELEASE.VERSION}.tar`);

	xlog.info`Removing existing version if necessary...`;
	await fileUtil.unlink(`${tarballFilePath}.bz2`);

	xlog.info`Generating readme.txt`;
	await fileUtil.writeTextFile(path.join(RELEASE.RELEASE_DIR, "readme.txt"), RELEASE.README_TEXT);

	xlog.info`Running ${fg.yellow("tar")} up ${RELEASE.VERSION} to ${tarballFilePath}`;
	await runUtil.run("tar", ["-cf", tarballFilePath, ...RELEASE.FILENAMES], {cwd : RELEASE.RELEASE_DIR, liveOutput : true});

	xlog.info`Running ${fg.yellow("pbzip2")}`;
	await runUtil.run("pbzip2", ["--force", "--verbose", path.basename(tarballFilePath)], {cwd : path.dirname(tarballFilePath), liveOutput : true});

	xlog.info`You can deploy the reelase by running ${fg.yellow("deployTelparia")}`;
}
