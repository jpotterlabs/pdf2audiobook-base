import { SignUp } from '@clerk/nextjs'

export function generateStaticParams() {
  return []
}

export default function SignUpPage() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignUp />
    </div>
  )
}
