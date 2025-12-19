'use client'

import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { createJob } from '../../lib/api'
import { Job } from '../../lib/types'
import toast, { Toaster } from 'react-hot-toast'
import { useAuth } from '@clerk/nextjs'

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [jobResponse, setJobResponse] = useState<Job | null>(null)
  const [voiceProvider, setVoiceProvider] = useState('openai')
  const [voiceType, setVoiceType] = useState('alloy')
  const [readingSpeed, setReadingSpeed] = useState(1.0)
  const [includeSummary, setIncludeSummary] = useState(true)
  const [conversionMode, setConversionMode] = useState('full')
  const { getToken } = useAuth()

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

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const token = await getToken()
      if (!token) {
        throw new Error('You must be signed in to upload a file.')
      }

      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('voice_provider', voiceProvider)
      formData.append('voice_type', voiceType)
      formData.append('reading_speed', readingSpeed.toString())
      formData.append('include_summary', includeSummary.toString())
      formData.append('conversion_mode', conversionMode)

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const response = await createJob(formData, token)

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
    } catch (error) {
      console.error('Upload failed:', error)
      toast.error(
        error instanceof Error
          ? error.message
          : 'Upload failed. Please try again.'
      )
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
              {/* Voice Provider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voice Provider
                </label>
                <select
                  value={voiceProvider}
                  onChange={(e) => setVoiceProvider(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900"
                >
                  <option value="openai">OpenAI</option>
                  <option value="google">Google Cloud</option>
                  <option value="eleven_labs">ElevenLabs</option>
                  <option value="azure">Azure Speech</option>
                  <option value="aws_polly">AWS Polly</option>
                </select>
              </div>

              {/* Voice Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voice
                </label>
                {voiceProvider === 'openai' ? (
                  <select
                    value={voiceType}
                    onChange={(e) => setVoiceType(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900"
                  >
                    <option value="alloy">Alloy (Neutral)</option>
                    <option value="echo">Echo (Male)</option>
                    <option value="fable">Fable (British)</option>
                    <option value="onyx">Onyx (Deep Male)</option>
                    <option value="nova">Nova (Femme)</option>
                    <option value="shimmer">Shimmer (Femme)</option>
                  </select>
                ) : voiceProvider === 'google' ? (
                  <select
                    value={voiceType}
                    onChange={(e) => setVoiceType(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900"
                  >
                    <optgroup label="Standard (Wavenet)">
                      <option value="us_female_std">US Female (Standard)</option>
                      <option value="us_male_std">US Male (Standard)</option>
                      <option value="gb_female_std">UK Female (Standard)</option>
                      <option value="gb_male_std">UK Male (Standard)</option>
                    </optgroup>
                    <optgroup label="Premium (Chirp/Studio)">
                      <option value="us_female_premium">US Female (Premium)</option>
                      <option value="us_male_premium">US Male (Premium)</option>
                      <option value="gb_female_premium">UK Female (Premium)</option>
                      <option value="gb_male_premium">UK Male (Premium)</option>
                    </optgroup>
                  </select>
                ) : (
                  <input
                    type="text"
                    value={voiceType}
                    onChange={(e) => setVoiceType(e.target.value)}
                    placeholder="Enter voice ID or name"
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900"
                  />
                )}
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

              {/* Conversion Mode */}
              <div className="md:col-span-2 space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Conversion Mode
                </label>
                <div className="flex flex-wrap gap-4">
                  {[
                    { id: 'full', label: 'Word-for-Word', desc: 'Convert the entire document text' },
                    { id: 'summary', label: 'Summary Only', desc: 'Convert an AI-generated summary' },
                    { id: 'explanation', label: 'Concept Explanation', desc: 'Explain core concepts in simple terms' }
                  ].map((mode) => (
                    <label key={mode.id} className={`flex-1 min-w-[200px] cursor-pointer border rounded-lg p-3 transition-all ${conversionMode === mode.id ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}>
                      <input
                        type="radio"
                        name="conversionMode"
                        value={mode.id}
                        checked={conversionMode === mode.id}
                        onChange={(e) => setConversionMode(e.target.value)}
                        className="sr-only"
                      />
                      <p className="font-semibold text-gray-900">{mode.label}</p>
                      <p className="text-xs text-gray-500 mt-1">{mode.desc}</p>
                    </label>
                  ))}
                </div>
              </div>

              {/* Include Summary (Only show if not in summary/explanation mode) */}
              {conversionMode === 'full' && (
                <div className="flex items-center md:col-span-2 mt-2">
                  <input
                    id="include-summary"
                    type="checkbox"
                    checked={includeSummary}
                    onChange={(e) => setIncludeSummary(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label
                    htmlFor="include-summary"
                    className="ml-2 block text-sm text-gray-900"
                  >
                    Prepend AI-generated summary to the full audio
                  </label>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload Button */}
        {selectedFile && !isUploading && !jobResponse && (
          <div className="mt-8 text-center">
            <button
              onClick={handleUpload}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold text-lg flex items-center space-x-2 mx-auto"
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

        {/* Error Handling */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <div className="flex items-center justify-center space-x-1">
            <AlertCircle className="h-4 w-4" />
            <span>
              Having trouble? Make sure you're signed in and your file is under
              50MB.
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
