package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
)

func main() {
	http.HandleFunc("/interface/module-post", module_load)
	err := http.ListenAndServe("0.0.0.0:8080", nil)
	if err != nil {
		print(err.Error())
	}
}

func module_load(w http.ResponseWriter, r *http.Request) {
	// Parse the multipart form data
	err := r.ParseMultipartForm(10 << 20) // 10 MB maximum file size
	if err != nil {
		http.Error(w, "Failed to parse form", http.StatusBadRequest)
		return
	}

	// Get the file from the form data
	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Failed to get file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create a new file on the server to save the uploaded file
	newFile, err := os.Create("/var/www/html/modules/" + handler.Filename)
	if err != nil {
		print(err.Error())
		http.Error(w, "Failed to create file", http.StatusInternalServerError)
		return
	}
	defer newFile.Close()

	// Copy the uploaded file data to the new file
	_, err = io.Copy(newFile, file)
	if err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "File uploaded successfully: %s\n", handler.Filename)
}
