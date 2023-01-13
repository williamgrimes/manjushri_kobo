SELECT
-- Bookmark.VolumeID,
Bookmark.Text,
--Bookmark.Annotation,
--Bookmark.ExtraAnnotationData,
Bookmark.DateCreated,
Bookmark.DateModified,
--content.BookTitle,
content.Title,
content.Attribution,
content.DateLastRead
FROM Bookmark
INNER JOIN content
ON Bookmark.VolumeID = content.ContentID;