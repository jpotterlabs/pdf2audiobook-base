"use client"

import type React from "react"

import { useCallback, useState } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileUploadZoneProps {
  onFileSelect: (file: File | null) => void
  selectedFile: File | null
}

export function FileUploadZone({ onFileSelect, selectedFile }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true)
    }
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = e.dataTransfer.files
      if (files && files.length > 0) {
        const file = files[0]
        if (file.type === "application/pdf") {
          onFileSelect(file)
        } else {
          alert("Please upload a PDF file")
        }
      }
    },
    [onFileSelect],
  )

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type === "application/pdf") {
        onFileSelect(file)
      } else {
        alert("Please upload a PDF file")
      }
    }
  }

  const handleRemove = () => {
    onFileSelect(null)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
  }

  return (
    <div>
      {!selectedFile ? (
        <div
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300 ${
            isDragging
              ? "border-primary bg-primary/10 scale-105"
              : "border-border hover:border-primary/50 hover:bg-muted/30"
          }`}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,application/pdf"
            onChange={handleFileInput}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <div className="space-y-2">
                <p className="text-lg font-semibold">{isDragging ? "Drop your PDF here" : "Drag and drop your PDF"}</p>
                <p className="text-sm text-muted-foreground">or click to browse</p>
              </div>
              <Button type="button" variant="outline" size="sm" className="mt-2 bg-transparent">
                Select File
              </Button>
              <p className="text-xs text-muted-foreground">Maximum file size: 50MB</p>
            </div>
          </label>
        </div>
      ) : (
        <div className="flex items-center gap-4 p-4 rounded-lg bg-muted/30 border border-border">
          <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
            <File className="w-6 h-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{selectedFile.name}</p>
            <p className="text-sm text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
          </div>
          <Button type="button" variant="ghost" size="sm" onClick={handleRemove}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
