'use client'

import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { createJob } from '../../lib/api'
import { Job } from '../../lib/types'
import toast, { Toaster } from 'react-hot-toast'

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [jobResponse, setJobResponse] = useState<Job | null>(null)
  const [voiceProvider, setVoiceProvider] = useState('openai')
  const [voiceType, setVoiceType] = useState('alloy')
  const [readingSpeed, setReadingSpeed] = useState(1.0)
  const [includeNarration, setIncludeNarration] = useState(true)
  const [includeSummary, setIncludeSummary] = useState(false)
  const [includeExplanation, setIncludeExplanation] = useState(false)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0])
        setJobResponse(null)
      }
    },
  })

  const handleUpload = async () => {
    if (!selectedFile) return

    if (!includeNarration && !includeSummary && !includeExplanation) {
      toast.error('Please select at least one output option.')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Determine Conversion Mode based on selections
      let mode = 'full'
      if (includeNarration) {
        if (includeExplanation) mode = 'full_explanation'
        // includeSummary is passed as a separate flag
      } else {
        if (includeSummary && includeExplanation) mode = 'summary_explanation'
        else if (includeExplanation) mode = 'explanation'
        else if (includeSummary) mode = 'summary'
      }

      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('voice_provider', voiceProvider)
      formData.append('voice_type', voiceType)
      formData.append('reading_speed', readingSpeed.toString())
      formData.append('include_summary', includeSummary.toString())
      formData.append('conversion_mode', mode)

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const response = await createJob(formData)

      clearInterval(progressInterval)
      setUploadProgress(100)
      setJobResponse(response)

      toast.success('PDF uploaded successfully! Processing will begin shortly.')

      // Reset after success
      setTimeout(() => {
        setSelectedFile(null)
        setUploadProgress(0)
        setJobResponse(null)
      }, 3000)
    } catch (error: any) {
      console.error('Upload failed:', error)
      toast.error(error?.message || 'Upload failed. Please try again.')
      setUploadProgress(0)
    } finally {
      setIsUploading(false)
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    setJobResponse(null)
    setUploadProgress(0)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Toaster position="top-right" />

      <div className="text-center mb-12">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Upload Your PDF
        </h1>
        <p className="text-xl text-gray-600">
          Convert your PDF documents to high-quality audiobooks
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${isDragActive
            ? 'border-blue-400 bg-blue-50'
            : selectedFile
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
            }`}
        >
          <input {...getInputProps()} />

          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-3">
                <FileText className="h-12 w-12 text-green-600" />
                <div className="text-left">
                  <p className="text-lg font-medium text-gray-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile()
                  }}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              {isUploading && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              )}

              {jobResponse && (
                <div className="flex items-center justify-center space-x-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span>Job created successfully! ID: {jobResponse.id}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-16 w-16 text-gray-400 mx-auto" />
              <div>
                <p className="text-xl font-medium text-gray-900">
                  {isDragActive
                    ? 'Drop your PDF here'
                    : 'Drag & drop your PDF here'}
                </p>
                <p className="text-gray-500 mt-2">or click to browse files</p>
              </div>
              <div className="text-sm text-gray-500">
                <p>Maximum file size: 50MB</p>
                <p>Supported format: PDF only</p>
              </div>
            </div>
          )}
        </div>

        {/* Settings Section */}
        {selectedFile && !isUploading && !jobResponse && (
          <div className="mt-8 space-y-6 border-t pt-8">
            <h3 className="text-lg font-semibold text-gray-900">
              Audiobook Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Voice Selection */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Provider & Voice
                </label>
                <div className="flex gap-4 mb-4">
                  <button
                    onClick={() => { setVoiceProvider('openai'); setVoiceType('alloy'); }}
                    className={`flex-1 py-2 rounded-md border ${voiceProvider === 'openai' ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-50 text-gray-700 border-gray-300'}`}
                  >
                    OpenAI
                  </button>
                  <button
                    onClick={() => { setVoiceProvider('google'); setVoiceType('en-US-Standard-C'); }}
                    className={`flex-1 py-2 rounded-md border ${voiceProvider === 'google' ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-50 text-gray-700 border-gray-300'}`}
                  >
                    Google
                  </button>
                </div>
                <select
                  value={voiceType}
                  onChange={(e) => setVoiceType(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900"
                >
                  {voiceProvider === 'openai' ? (
                    <>
                      <option value="alloy">Alloy</option>
                      <option value="echo">Echo</option>
                      <option value="fable">Fable</option>
                      <option value="onyx">Onyx</option>
                      <option value="nova">Nova</option>
                      <option value="shimmer">Shimmer</option>
                    </>
                  ) : (
                    <>
                      <option value="en-US-Standard-C">Standard Female (C)</option>
                      <option value="en-US-Standard-D">Standard Male (D)</option>
                      <option value="en-US-Wavenet-C">Wavenet Female (C)</option>
                      <option value="en-US-Wavenet-D">Wavenet Male (D)</option>
                    </>
                  )}
                </select>
              </div>

              {/* Reading Speed */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reading Speed ({readingSpeed}x)
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={readingSpeed}
                  onChange={(e) => setReadingSpeed(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {/* Output Options */}
              <div className="md:col-span-2 space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Audio Output Options
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Full Narration */}
                  <label className={`flex items-start p-3 border rounded-lg cursor-pointer transition-all ${includeNarration ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input
                      type="checkbox"
                      checked={includeNarration}
                      onChange={(e) => setIncludeNarration(e.target.checked)}
                      className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <span className="block text-sm font-semibold text-gray-900">Word-for-Word</span>
                      <span className="block text-xs text-gray-500 mt-1">Full commercial extraction</span>
                    </div>
                  </label>

                  {/* Summary */}
                  <label className={`flex items-start p-3 border rounded-lg cursor-pointer transition-all ${includeSummary ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input
                      type="checkbox"
                      checked={includeSummary}
                      onChange={(e) => setIncludeSummary(e.target.checked)}
                      className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <span className="block text-sm font-semibold text-gray-900">AI Summary</span>
                      <span className="block text-xs text-gray-500 mt-1">Concise overview of content</span>
                    </div>
                  </label>

                  {/* Explanation */}
                  <label className={`flex items-start p-3 border rounded-lg cursor-pointer transition-all ${includeExplanation ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input
                      type="checkbox"
                      checked={includeExplanation}
                      onChange={(e) => setIncludeExplanation(e.target.checked)}
                      className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <span className="block text-sm font-semibold text-gray-900">Concept Explanation</span>
                      <span className="block text-xs text-gray-500 mt-1">Educational breakdown</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Button */}
        {selectedFile && !isUploading && !jobResponse && (
          <div className="mt-8 text-center">
            <button
              onClick={handleUpload}
              className="px-8 py-3 rounded-lg font-semibold text-lg flex items-center space-x-2 mx-auto bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Upload className="h-5 w-5" />
              <span>Start Conversion</span>
            </button>
          </div>
        )}

        {/* Processing Status */}
        {isUploading && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center space-x-2 text-blue-600">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <span>Processing your PDF...</span>
            </div>
          </div>
        )}

        {/* Job Response */}
        {jobResponse && (
          <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800">Upload Successful!</p>
                <p className="text-sm text-green-700">
                  Job ID: {jobResponse.id} - Status: {jobResponse.status}
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Check your jobs page to monitor progress.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
