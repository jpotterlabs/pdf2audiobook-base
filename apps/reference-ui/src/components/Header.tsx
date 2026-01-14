'use client'

import Link from 'next/link'
import { FileText, Upload, History, CreditCard } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <FileText className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">
              PDF2AudioBook
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link
              href="/upload"
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
            >
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </Link>
            <Link
              href="/jobs"
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
            >
              <History className="h-4 w-4" />
              <span>My Jobs</span>
            </Link>
          </nav>

          {/* User Display (Mock) */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-100">
              <span className="text-[10px] font-bold uppercase tracking-wider mr-2">
                Base User
              </span>
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-[10px]">
                BU
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
