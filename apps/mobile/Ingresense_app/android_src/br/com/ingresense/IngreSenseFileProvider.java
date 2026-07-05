package br.com.ingresense;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;

public class IngreSenseFileProvider extends ContentProvider {
    public static final String AUTHORITY = "br.com.ingresense.fileprovider";
    private static final String CAPTURE_PATH = "/capture/captured_label.jpg";

    public static File getCaptureFile(Context context) {
        File imagesDir = new File(context.getCacheDir(), "images");
        imagesDir.mkdirs();
        return new File(imagesDir, "captured_label.jpg");
    }

    public static Uri getUriForCapture(Context context) {
        return Uri.parse("content://" + AUTHORITY + CAPTURE_PATH);
    }

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public String getType(Uri uri) {
        return "image/jpeg";
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        File file = resolveFile(uri);
        int accessMode = ParcelFileDescriptor.MODE_READ_ONLY;

        if (mode != null && mode.contains("w")) {
            accessMode = ParcelFileDescriptor.MODE_READ_WRITE
                    | ParcelFileDescriptor.MODE_CREATE
                    | ParcelFileDescriptor.MODE_TRUNCATE;
        }

        return ParcelFileDescriptor.open(file, accessMode);
    }

    @Override
    public Cursor query(
            Uri uri,
            String[] projection,
            String selection,
            String[] selectionArgs,
            String sortOrder) {
        File file;
        try {
            file = resolveFile(uri);
        } catch (FileNotFoundException e) {
            return null;
        }

        MatrixCursor cursor = new MatrixCursor(new String[] {
                OpenableColumns.DISPLAY_NAME,
                OpenableColumns.SIZE
        });
        cursor.addRow(new Object[] {file.getName(), file.length()});
        return cursor;
    }

    @Override
    public Uri insert(Uri uri, ContentValues values) {
        return null;
    }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {
        return 0;
    }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        return 0;
    }

    private File resolveFile(Uri uri) throws FileNotFoundException {
        if (!AUTHORITY.equals(uri.getAuthority()) || !CAPTURE_PATH.equals(uri.getPath())) {
            throw new FileNotFoundException("URI nao suportada: " + uri);
        }

        Context context = getContext();
        if (context == null) {
            throw new FileNotFoundException("Contexto Android indisponivel.");
        }

        return getCaptureFile(context);
    }
}
